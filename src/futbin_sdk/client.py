"""FUTBIN API Client"""

import asyncio
from typing import Any

import httpx
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


class FutbinClient:
    """FUTBIN API 客户端

    支持同步和异步调用方式。

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
    ):
        self.timeout = timeout
        self.proxy = proxy
        self._custom_headers = headers or {}
        self._async_client: httpx.AsyncClient | None = None
        self._sync_client: httpx.Client | None = None

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

    # =========================================================================
    # Player Price APIs
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
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
        url = f"{FUTBIN_API_BASE}/getPlayersPrice"
        params = {"player_ids": str(player_id), "platform": platform.value}

        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()

        data = resp.json()
        player_data = data.get(str(player_id), {}).get("prices", {}).get(platform.value, {})
        return PlayerPrice.from_api_response(player_data)

    def get_player_price_sync(
        self,
        player_id: int | str,
        platform: Platform = Platform.PS,
    ) -> PlayerPrice:
        """同步获取球员价格"""
        return asyncio.get_event_loop().run_until_complete(self.get_player_price(player_id, platform))

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
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
        url = f"{FUTBIN_API_BASE}/fetchPriceInformation"
        params = {"playerresource": str(resource_id), "platform": platform.value}

        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()

        data = resp.json()
        return PlayerPrice(
            price=int(data.get("price", 0) or 0),
            min_price=int(data.get("MinPrice", 0) or 0),
            max_price=int(data.get("MaxPrice", 0) or 0),
        )

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
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
        url = f"{FUTBIN_API_BASE}/getPlayersPrice"
        ids_str = ",".join(str(pid) for pid in player_ids)
        params = {"player_ids": ids_str, "platform": platform.value}

        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()

        data = resp.json()
        result: dict[str, PlayerPrice] = {}

        for pid in player_ids:
            pid_str = str(pid)
            player_data = data.get(pid_str, {}).get("prices", {}).get(platform.value, {})
            result[pid_str] = PlayerPrice.from_api_response(player_data)

        return result

    # =========================================================================
    # Popular Players API
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def get_popular_players(self) -> list[PopularPlayer]:
        """获取热门球员列表

        Returns:
            PopularPlayer 列表
        """
        url = f"{FUTBIN_API_BASE}/getPopularPlayers"

        resp = await self.async_client.get(url)
        resp.raise_for_status()

        data = resp.json()
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

        return players

    # =========================================================================
    # Search / Filter Players API
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
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
        url = f"{FUTBIN_API_BASE}/getFilteredPlayers"

        if options:
            params = options.to_params()
        else:
            params = {"platform": "PS", "page": 1, **kwargs}

        resp = await self.async_client.get(url, params=params)
        resp.raise_for_status()

        data = resp.json()
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        return players

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def get_totw(self) -> list[FullPlayer]:
        """获取本周最佳球员 (Team of the Week)

        Returns:
            FullPlayer 列表
        """
        url = f"{FUTBIN_API_BASE}/currentTOTW"

        resp = await self.async_client.get(url)
        resp.raise_for_status()

        data = resp.json()
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        return players

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def get_latest_players(self) -> list[FullPlayer]:
        """获取最新球员

        Returns:
            FullPlayer 列表
        """
        url = f"{FUTBIN_API_BASE}/newPlayers"

        resp = await self.async_client.get(url)
        resp.raise_for_status()

        data = resp.json()
        players: list[FullPlayer] = []

        for item in data.get("data", []):
            players.append(FullPlayer.from_api_response(item))

        return players

    # =========================================================================
    # Leagues & Clubs API
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def get_leagues_and_clubs(self) -> list[League]:
        """获取所有联赛和俱乐部

        Returns:
            League 列表（每个联赛包含其俱乐部）
        """
        url = f"{FUTBIN_API_BASE}/getLeaguesAndClubsAndroid"

        resp = await self.async_client.get(url)
        resp.raise_for_status()

        data = resp.json()
        leagues: list[League] = []

        for item in data.get("data", []):
            leagues.append(League.from_api_response(item))

        return leagues

    # =========================================================================
    # Card Versions API
    # =========================================================================

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_fixed(DEFAULT_RETRY_DELAY),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    )
    async def get_card_versions(self) -> list[CardVersionInfo]:
        """获取所有卡片版本

        Returns:
            CardVersionInfo 列表
        """
        url = f"{FUTBIN_API_BASE}/getCardVersions"

        resp = await self.async_client.get(url)
        resp.raise_for_status()

        data = resp.json()
        versions: list[CardVersionInfo] = []

        for item in data.get("data", []):
            versions.append(CardVersionInfo.from_api_response(item))

        return versions

    # =========================================================================
    # Consumables API (requires web scraping)
    # =========================================================================

    async def get_chemistry_styles(self) -> list[ChemistryStyle]:
        """获取化学卡价格列表

        注意：此 API 需要爬取网页，可能需要代理绕过 Cloudflare

        Returns:
            ChemistryStyle 列表
        """
        # TODO: 实现网页爬取
        raise NotImplementedError("Chemistry styles API requires web scraping implementation")

    async def get_manager_cards(self) -> list[ManagerCard]:
        """获取教练员卡价格列表

        注意：此 API 需要爬取网页，可能需要代理绕过 Cloudflare

        Returns:
            ManagerCard 列表
        """
        # TODO: 实现网页爬取
        raise NotImplementedError("Manager cards API requires web scraping implementation")
