"""FUTBIN API Client"""

import asyncio
import concurrent.futures
from typing import Any, cast

import httpx
from bs4 import BeautifulSoup
from cachetools import TTLCache  # type: ignore[import-untyped]
from fake_useragent import UserAgent
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from futbin_sdk.models import (
    CardVersionInfo,
    ChemistryStyle,
    FullPlayer,
    League,
    ManagerCard,
    Platform,
    PlayerPrice,
    PlayerSearchOptions,
    PopularPlayer,
)

# API Base URLs
FUTBIN_API_BASE = "https://www.futbin.org/futbin/api"
FUTBIN_WEB_BASE = "https://www.futbin.com"

# 默认配置
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 2
DEFAULT_CACHE_TTL = 180  # 3 分钟缓存
DEFAULT_CACHE_MAXSIZE = 1000

# User Agent 生成器
_ua = UserAgent()



def _get_default_headers() -> dict[str, str]:
    """获取默认请求头（随机 User-Agent）"""
    return {
        "User-Agent": _ua.random,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.futbin.com/",
        "Origin": "https://www.futbin.com",
    }


class FutbinError(Exception):
    """FUTBIN API 错误"""

    pass


def _run_sync(client: "FutbinClient", coro_func: Any, *args: Any, **kwargs: Any) -> Any:
    """同步运行协程（为每次调用重置 async_client）

    Args:
        client: FutbinClient 实例
        coro_func: 返回协程的可调用对象
        *args, **kwargs: 传递给 coro_func 的参数
    """
    # 重置 async_client 避免 event loop 问题
    if client._async_client is not None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # 不在运行的 loop 中，需要重置 client
            client._async_client = None

    async def run_with_cleanup() -> Any:
        try:
            return await coro_func(*args, **kwargs)
        finally:
            # 确保关闭 client
            if client._async_client is not None:
                await client._async_client.aclose()
                client._async_client = None

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, run_with_cleanup())
            return future.result()
    return asyncio.run(run_with_cleanup())


class FutbinClient:
    """FUTBIN API 客户端

    支持同步和异步调用方式，内置 TTL 缓存。

    Usage:
        # 异步使用
        async with FutbinClient() as client:
            price = await client.get_player_price(12345, Platform.PS)

        # 同步使用
        client = FutbinClient()
        price = client.get_player_price_sync(12345, Platform.PS)
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        proxy: str | None = None,
        headers: dict[str, str] | None = None,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        cache_maxsize: int = DEFAULT_CACHE_MAXSIZE,
        enable_cache: bool = True,
    ):
        self.timeout = timeout
        self.proxy = proxy
        self._custom_headers = headers or {}
        self._async_client: httpx.AsyncClient | None = None
        self._sync_client: httpx.Client | None = None
        self._enable_cache = enable_cache
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    def _get_headers(self) -> dict[str, str]:
        """获取请求头（每次调用生成新的随机 UA）"""
        return {**_get_default_headers(), **self._custom_headers}

    async def __aenter__(self) -> "FutbinClient":
        self._async_client = httpx.AsyncClient(
            timeout=self.timeout,
            proxy=self.proxy,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> "FutbinClient":
        self._sync_client = httpx.Client(
            timeout=self.timeout,
            proxy=self.proxy,
            headers=self._get_headers(),
        )
        return self

    def __exit__(self, *args: Any) -> None:
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    @property
    def async_client(self) -> httpx.AsyncClient:
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                proxy=self.proxy,
                headers=self._get_headers(),
            )
        return self._async_client

    @property
    def sync_client(self) -> httpx.Client:
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                proxy=self.proxy,
                headers=self._get_headers(),
            )
        return self._sync_client

    def _get_cache_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        """生成缓存键"""
        key_parts = [method, *[str(a) for a in args], *[f"{k}={v}" for k, v in sorted(kwargs.items())]]
        return ":".join(key_parts)

    def _get_from_cache(self, key: str) -> Any:
        """从缓存获取"""
        if not self._enable_cache:
            return None
        return self._cache.get(key)

    def _set_to_cache(self, key: str, value: Any) -> None:
        """设置缓存"""
        if self._enable_cache:
            self._cache[key] = value

    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()

    # =========================================================================
    # 内部请求方法
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def _api_get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """发送 API GET 请求"""
        url = f"{FUTBIN_API_BASE}/{endpoint}"
        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def _web_get(self, path: str, params: dict[str, Any] | None = None) -> str:
        """发送网页 GET 请求"""
        url = f"{FUTBIN_WEB_BASE}/{path}"
        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()
        return resp.text

    # =========================================================================
    # Player Price APIs
    # =========================================================================

    async def get_player_price(
        self,
        player_id: int | str,
        platform: Platform = Platform.PS,
    ) -> PlayerPrice:
        """通过 FUTBIN ID 获取球员价格

        Args:
            player_id: FUTBIN 球员 ID
            platform: 游戏平台 (PS/PC/XB)

        Returns:
            PlayerPrice 对象
        """
        cache_key = self._get_cache_key("get_player_price", player_id, platform.value)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(PlayerPrice, cached)

        params = {"player_ids": str(player_id), "platform": platform.value}
        data = await self._api_get("getPlayersPrice", params)
        player_data = data.get(str(player_id), {}).get("prices", {}).get(platform.value, {})
        result = PlayerPrice.from_api_response(player_data)

        self._set_to_cache(cache_key, result)
        return result

    def get_player_price_sync(
        self,
        player_id: int | str,
        platform: Platform = Platform.PS,
    ) -> PlayerPrice:
        """同步获取球员价格"""
        return cast(PlayerPrice, _run_sync(self, self.get_player_price, player_id, platform))

    async def get_player_price_by_resource_id(
        self,
        resource_id: int | str,
        platform: Platform = Platform.PS,
    ) -> PlayerPrice:
        """通过 EA Resource ID 获取球员价格

        Args:
            resource_id: EA Resource ID
            platform: 游戏平台

        Returns:
            PlayerPrice 对象
        """
        cache_key = self._get_cache_key("get_player_price_by_resource_id", resource_id, platform.value)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(PlayerPrice, cached)

        params = {"playerresource": str(resource_id), "platform": platform.value}
        data = await self._api_get("fetchPriceInformation", params)
        result = PlayerPrice(
            price=int(data.get("price", 0) or 0),
            min_price=int(data.get("MinPrice", 0) or 0),
            max_price=int(data.get("MaxPrice", 0) or 0),
        )

        self._set_to_cache(cache_key, result)
        return result

    def get_player_price_by_resource_id_sync(
        self,
        resource_id: int | str,
        platform: Platform = Platform.PS,
    ) -> PlayerPrice:
        """同步通过 EA Resource ID 获取球员价格"""
        return cast(PlayerPrice, _run_sync(self, self.get_player_price_by_resource_id, resource_id, platform))

    async def get_players_prices(
        self,
        player_ids: list[int | str],
        platform: Platform = Platform.PS,
    ) -> dict[str, PlayerPrice]:
        """批量获取球员价格

        Args:
            player_ids: FUTBIN 球员 ID 列表
            platform: 游戏平台

        Returns:
            {player_id: PlayerPrice} 字典
        """
        cache_key = self._get_cache_key("get_players_prices", ",".join(map(str, player_ids)), platform.value)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(dict[str, PlayerPrice], cached)

        params = {"player_ids": ",".join(str(pid) for pid in player_ids), "platform": platform.value}
        data = await self._api_get("getPlayersPrice", params)

        result: dict[str, PlayerPrice] = {}
        for pid in player_ids:
            pid_str = str(pid)
            player_data = data.get(pid_str, {}).get("prices", {}).get(platform.value, {})
            result[pid_str] = PlayerPrice.from_api_response(player_data)

        self._set_to_cache(cache_key, result)
        return result

    def get_players_prices_sync(
        self,
        player_ids: list[int | str],
        platform: Platform = Platform.PS,
    ) -> dict[str, PlayerPrice]:
        """同步批量获取球员价格"""
        return cast(dict[str, PlayerPrice], _run_sync(self, self.get_players_prices, player_ids, platform))

    async def get_players_prices_concurrent(
        self,
        player_ids: list[int | str],
        platform: Platform = Platform.PS,
        batch_size: int = 50,
        max_concurrency: int = 5,
    ) -> dict[str, PlayerPrice]:
        """并发批量获取球员价格（大量球员时使用）

        Args:
            player_ids: FUTBIN 球员 ID 列表
            platform: 游戏平台
            batch_size: 每批大小
            max_concurrency: 最大并发数

        Returns:
            {player_id: PlayerPrice} 字典
        """
        semaphore = asyncio.Semaphore(max_concurrency)
        batches = [player_ids[i : i + batch_size] for i in range(0, len(player_ids), batch_size)]

        async def fetch_batch(batch: list[int | str]) -> dict[str, PlayerPrice]:
            async with semaphore:
                return await self.get_players_prices(batch, platform)

        results = await asyncio.gather(*[fetch_batch(batch) for batch in batches])
        merged: dict[str, PlayerPrice] = {}
        for batch_result in results:
            merged.update(batch_result)
        return merged

    # =========================================================================
    # Popular Players API
    # =========================================================================

    async def get_popular_players(self) -> list[PopularPlayer]:
        """获取热门球员列表

        Returns:
            PopularPlayer 列表
        """
        cache_key = self._get_cache_key("get_popular_players")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[PopularPlayer], cached)

        data = await self._api_get("getPopularPlayers")
        players: list[PopularPlayer] = []

        for item in data.get("data", []):
            players.append(
                PopularPlayer(
                    futbin_id=int(item.get("ID", 0)),
                    resource_id=int(item.get("resource_id", 0)),
                    name=item.get("name", ""),
                    rating=int(item.get("rating", 0)),
                    price_ps=int(item.get("ps_LCPrice", 0) or 0),
                    price_pc=int(item.get("pc_LCPrice", 0) or 0),
                )
            )

        self._set_to_cache(cache_key, players)
        return players

    def get_popular_players_sync(self) -> list[PopularPlayer]:
        """同步获取热门球员列表"""
        return cast(list[PopularPlayer], _run_sync(self, self.get_popular_players, ))

    # =========================================================================
    # Search / Filter Players API
    # =========================================================================

    async def search_players(
        self,
        options: PlayerSearchOptions | None = None,
        **kwargs: Any,
    ) -> list[FullPlayer]:
        """搜索球员

        Args:
            options: 搜索选项对象
            **kwargs: 直接传入搜索参数

        Returns:
            FullPlayer 列表
        """
        if options:
            params = options.to_params()
        else:
            params = {"platform": "PS", "page": 1, **kwargs}

        data = await self._api_get("getFilteredPlayers", params)
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        return players

    def search_players_sync(
        self,
        options: PlayerSearchOptions | None = None,
        **kwargs: Any,
    ) -> list[FullPlayer]:
        """同步搜索球员"""
        return cast(list[FullPlayer], _run_sync(self, self.search_players, options, **kwargs))

    async def get_totw(self) -> list[FullPlayer]:
        """获取本周最佳球员 (Team of the Week)

        Returns:
            FullPlayer 列表
        """
        cache_key = self._get_cache_key("get_totw")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[FullPlayer], cached)

        data = await self._api_get("currentTOTW")
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        self._set_to_cache(cache_key, players)
        return players

    def get_totw_sync(self) -> list[FullPlayer]:
        """同步获取本周最佳球员"""
        return cast(list[FullPlayer], _run_sync(self, self.get_totw, ))

    async def get_latest_players(self) -> list[FullPlayer]:
        """获取最新球员

        Returns:
            FullPlayer 列表
        """
        cache_key = self._get_cache_key("get_latest_players")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[FullPlayer], cached)

        data = await self._api_get("newPlayers")
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        self._set_to_cache(cache_key, players)
        return players

    def get_latest_players_sync(self) -> list[FullPlayer]:
        """同步获取最新球员"""
        return cast(list[FullPlayer], _run_sync(self, self.get_latest_players, ))

    # =========================================================================
    # Leagues & Clubs API
    # =========================================================================

    async def get_leagues_and_clubs(self) -> list[League]:
        """获取所有联赛和俱乐部

        Returns:
            League 列表（每个联赛包含其俱乐部）
        """
        cache_key = self._get_cache_key("get_leagues_and_clubs")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[League], cached)

        data = await self._api_get("getLeaguesAndClubsAndroid")
        leagues: list[League] = []

        for item in data.get("data", []):
            leagues.append(League.from_api_response(item))

        self._set_to_cache(cache_key, leagues)
        return leagues

    def get_leagues_and_clubs_sync(self) -> list[League]:
        """同步获取所有联赛和俱乐部"""
        return cast(list[League], _run_sync(self, self.get_leagues_and_clubs, ))

    # =========================================================================
    # Card Versions API
    # =========================================================================

    async def get_card_versions(self) -> list[CardVersionInfo]:
        """获取所有卡片版本

        Returns:
            CardVersionInfo 列表
        """
        cache_key = self._get_cache_key("get_card_versions")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[CardVersionInfo], cached)

        data = await self._api_get("getCardVersions")
        versions: list[CardVersionInfo] = []

        for item in data.get("data", []):
            versions.append(CardVersionInfo.from_api_response(item))

        self._set_to_cache(cache_key, versions)
        return versions

    def get_card_versions_sync(self) -> list[CardVersionInfo]:
        """同步获取所有卡片版本"""
        return cast(list[CardVersionInfo], _run_sync(self, self.get_card_versions, ))

    # =========================================================================
    # Consumables API (Web Scraping)
    # =========================================================================

    def _parse_price_text(self, text: str) -> int:
        """解析价格文本（支持 K/M 后缀）"""
        if not text:
            return 0
        text = text.strip().upper().replace(",", "")
        try:
            if text.endswith("K"):
                return int(float(text[:-1]) * 1000)
            elif text.endswith("M"):
                return int(float(text[:-1]) * 1000000)
            return int(float(text))
        except (ValueError, TypeError):
            return 0

    async def get_chemistry_styles(self, platform: Platform = Platform.PS) -> list[ChemistryStyle]:
        """获取化学卡价格列表

        Args:
            platform: 游戏平台

        Returns:
            ChemistryStyle 列表
        """
        cache_key = self._get_cache_key("get_chemistry_styles", platform.value)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[ChemistryStyle], cached)

        html = await self._web_get("consumables/Chemistry%20Styles")
        soup = BeautifulSoup(html, "html.parser")
        styles: list[ChemistryStyle] = []

        # 查找表格 (class="players-table" 或 id="consumables-table")
        table = soup.find("table", class_="players-table")
        if not table:
            table = soup.find("table", {"id": "consumables-table"})
        if not table:
            return styles

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 9:
                continue

            name = cols[0].get_text(strip=True)
            # 表格结构: 名称, PS价格, PC价格, PS最低, PC最低, PS最高, PC最高, 加成, 位置
            ps_price = self._parse_price_text(cols[1].get_text(strip=True))
            pc_price = self._parse_price_text(cols[2].get_text(strip=True))
            min_price_ps = self._parse_price_text(cols[3].get_text(strip=True))
            min_price_pc = self._parse_price_text(cols[4].get_text(strip=True))
            max_price_ps = self._parse_price_text(cols[5].get_text(strip=True))
            max_price_pc = self._parse_price_text(cols[6].get_text(strip=True))
            boost = cols[7].get_text(strip=True) if len(cols) > 7 else ""
            position = cols[8].get_text(strip=True) if len(cols) > 8 else ""

            styles.append(
                ChemistryStyle(
                    name=name,
                    price_ps=ps_price,
                    price_pc=pc_price,
                    min_price_ps=min_price_ps,
                    min_price_pc=min_price_pc,
                    max_price_ps=max_price_ps,
                    max_price_pc=max_price_pc,
                    boost=boost,
                    preferred_positions=[position] if position else [],
                )
            )

        self._set_to_cache(cache_key, styles)
        return styles

    def get_chemistry_styles_sync(self, platform: Platform = Platform.PS) -> list[ChemistryStyle]:
        """同步获取化学卡价格列表"""
        return cast(list[ChemistryStyle], _run_sync(self, self.get_chemistry_styles, platform))

    async def get_manager_cards(self, platform: Platform = Platform.PS) -> list[ManagerCard]:
        """获取教练员卡价格列表

        Args:
            platform: 游戏平台

        Returns:
            ManagerCard 列表
        """
        cache_key = self._get_cache_key("get_manager_cards", platform.value)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cast(list[ManagerCard], cached)

        html = await self._web_get("manager-prices")
        soup = BeautifulSoup(html, "html.parser")
        managers: list[ManagerCard] = []

        # 查找表格 (class="players-table" 或 id="managers-table")
        table = soup.find("table", class_="players-table")
        if not table:
            table = soup.find("table", {"id": "managers-table"})
        if not table:
            return managers

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            nation = cols[0].get_text(strip=True)

            # 表格结构可能是 6 列或 7 列:
            # 国家, 铜PS, 铜PC, 银PS, 银PC, 金PS, 金PC
            # 某些国家没有铜卡时可能显示 "-"
            def get_col_price(columns: list[Any], idx: int) -> int:
                if idx < len(columns):
                    text = columns[idx].get_text(strip=True)
                    if text == "-":
                        return 0
                    return self._parse_price_text(text)
                return 0

            bronze_ps = get_col_price(cols, 1)
            bronze_pc = get_col_price(cols, 2)
            silver_ps = get_col_price(cols, 3)
            silver_pc = get_col_price(cols, 4)
            gold_ps = get_col_price(cols, 5)
            gold_pc = get_col_price(cols, 6)

            managers.append(
                ManagerCard(
                    nation=nation,
                    bronze_price_ps=bronze_ps,
                    bronze_price_pc=bronze_pc,
                    silver_price_ps=silver_ps,
                    silver_price_pc=silver_pc,
                    gold_price_ps=gold_ps,
                    gold_price_pc=gold_pc,
                )
            )

        self._set_to_cache(cache_key, managers)
        return managers

    def get_manager_cards_sync(self, platform: Platform = Platform.PS) -> list[ManagerCard]:
        """同步获取教练员卡价格列表"""
        return cast(list[ManagerCard], _run_sync(self, self.get_manager_cards, platform))
