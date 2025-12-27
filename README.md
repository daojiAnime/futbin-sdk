# FUTBIN SDK

[![PyPI version](https://badge.fury.io/py/futbin-sdk.svg)](https://badge.fury.io/py/futbin-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/futbin-sdk.svg)](https://pypi.org/project/futbin-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Unofficial** Python SDK for FUTBIN API - Access FIFA Ultimate Team player prices and statistics.

## Installation

```bash
pip install futbin-sdk
```

## Quick Start

### Async Usage

```python
import asyncio
from futbin_sdk import FutbinClient, Platform

async def main():
    async with FutbinClient() as client:
        # 获取单个球员价格
        price = await client.get_player_price(12345, Platform.PS)
        print(f"Price: {price.price}")

        # 批量获取价格
        prices = await client.get_players_prices([12345, 67890], Platform.PS)
        for pid, p in prices.items():
            print(f"Player {pid}: {p.price}")

        # 获取热门球员
        popular = await client.get_popular_players()
        for player in popular[:5]:
            print(f"{player.name}: {player.price_ps}")

asyncio.run(main())
```

### Sync Usage

```python
from futbin_sdk import FutbinClient, Platform

client = FutbinClient()
price = client.get_player_price_sync(12345, Platform.PS)
print(f"Price: {price.price}")
```

## API Reference

### FutbinClient

| Method | Description |
|--------|-------------|
| `get_player_price(player_id, platform)` | 通过 FUTBIN ID 获取球员价格 |
| `get_player_price_by_resource_id(resource_id, platform)` | 通过 EA Resource ID 获取价格 |
| `get_players_prices(player_ids, platform)` | 批量获取球员价格 |
| `get_popular_players()` | 获取热门球员列表 |

### Models

- `PlayerPrice` - 球员价格信息 (price, min_price, max_price)
- `Player` - 球员完整信息
- `PopularPlayer` - 热门球员
- `Platform` - 游戏平台枚举 (PS, PC, XBOX)

## Configuration

```python
client = FutbinClient(
    timeout=30,           # 请求超时(秒)
    proxy="http://...",   # 代理地址
    headers={...},        # 自定义请求头
)
```

## Disclaimer

This is an **unofficial** SDK. FUTBIN does not provide a public API, and this SDK uses reverse-engineered endpoints that may change without notice.

- Use responsibly and respect FUTBIN's terms of service
- Do not use for commercial purposes without permission
- Rate limit your requests to avoid IP bans

## License

MIT License - see [LICENSE](LICENSE) for details.
