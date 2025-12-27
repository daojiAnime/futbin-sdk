# FUTBIN SDK

[![PyPI version](https://badge.fury.io/py/futbin-sdk.svg)](https://badge.fury.io/py/futbin-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/futbin-sdk.svg)](https://pypi.org/project/futbin-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Unofficial** Python SDK for FUTBIN API - Access FIFA Ultimate Team (EA FC) player prices, statistics, and more.

Inspired by [matheusfm/futbin](https://github.com/matheusfm/futbin) (Go) and [rfutbin](https://github.com/danielredondo/rfutbin) (R).

## Installation

```bash
pip install futbin-sdk
```

Or with uv:

```bash
uv add futbin-sdk
```

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from futbin_sdk import FutbinClient, Platform, PlayerSearchOptions

async def main():
    async with FutbinClient() as client:
        # Get popular players
        popular = await client.get_popular_players()
        for player in popular[:5]:
            print(f"{player.name}: {player.price_ps:,} coins")

        # Get player price by FUTBIN ID
        price = await client.get_player_price(12345, Platform.PS)
        print(f"Price: {price.price:,}")

        # Search players with filters
        options = PlayerSearchOptions(
            platform="PS",
            min_rating=85,
            position=["ST", "CF"],
        )
        players = await client.search_players(options=options)

        # Get Team of the Week
        totw = await client.get_totw()

        # Get latest players
        latest = await client.get_latest_players()

        # Get all leagues and clubs
        leagues = await client.get_leagues_and_clubs()

        # Get card versions (TOTW, TOTY, Icons, etc.)
        versions = await client.get_card_versions()

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

### Player APIs

| Method | Description |
|--------|-------------|
| `get_player_price(player_id, platform)` | Get price by FUTBIN ID |
| `get_player_price_by_resource_id(resource_id, platform)` | Get price by EA Resource ID |
| `get_players_prices(player_ids, platform)` | Batch get prices |
| `get_popular_players()` | Get trending players |
| `search_players(options)` | Search with filters |
| `get_totw()` | Get Team of the Week |
| `get_latest_players()` | Get newly added players |

### Reference Data APIs

| Method | Description |
|--------|-------------|
| `get_leagues_and_clubs()` | Get all leagues with their clubs |
| `get_card_versions()` | Get all card versions (TOTW, Icons, etc.) |

### Search Options

`PlayerSearchOptions` supports:

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | str | Platform: "PS" or "PC" |
| `page` | int | Page number (default: 1) |
| `version` | str | Card version filter |
| `position` | list[str] | Position filter (e.g., ["ST", "CF"]) |
| `nation_id` | int | Nation ID filter |
| `league_id` | int | League ID filter |
| `club_id` | int | Club ID filter |
| `min_rating` | int | Minimum rating |
| `max_rating` | int | Maximum rating |
| `min_price` | int | Minimum price |
| `max_price` | int | Maximum price |

## Models

| Model | Description |
|-------|-------------|
| `PlayerPrice` | Price info (price, min_price, max_price) |
| `PopularPlayer` | Popular player with basic info |
| `FullPlayer` | Complete player info (30+ fields) |
| `League` | League with clubs list |
| `Club` | Club info |
| `CardVersionInfo` | Card version (TOTW, TOTY, etc.) |
| `Platform` | Platform enum (PS, PC, XBOX) |
| `Position` | Position enum (GK, CB, ST, etc.) |

## Configuration

```python
client = FutbinClient(
    timeout=30,           # Request timeout (seconds)
    proxy="http://...",   # Proxy URL
    headers={...},        # Custom headers
)
```

## Feature Comparison

| Feature | futbin-sdk (Python) | matheusfm/futbin (Go) | rfutbin (R) |
|---------|--------------------|-----------------------|-------------|
| Player prices | ✅ | ✅ | ✅ |
| Search/filter players | ✅ | ✅ | ✅ |
| Popular players | ✅ | ✅ | ❌ |
| TOTW players | ✅ | ✅ | ❌ |
| Latest players | ✅ | ✅ | ❌ |
| Leagues & Clubs | ✅ | ✅ | ❌ |
| Card versions | ✅ | ✅ | ❌ |
| Nations data | 🔜 | ✅ | ❌ |
| Async support | ✅ | ❌ | ❌ |
| Type hints | ✅ | ✅ | ❌ |

## Disclaimer

This is an **unofficial** SDK. FUTBIN does not provide a public API, and this SDK uses reverse-engineered endpoints that may change without notice.

- Use responsibly and respect FUTBIN's terms of service
- Rate limit your requests to avoid IP bans
- Do not use for commercial purposes without permission

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
