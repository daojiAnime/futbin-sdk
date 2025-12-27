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
from futbin_sdk import FutbinClient, Platform, PlayerSearchOptions, get_nation_name

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

        # Advanced search with detailed attributes
        options = PlayerSearchOptions(
            platform="PS",
            min_pace=90,
            min_shooting=85,
            min_skills=4,
            min_weak_foot=4,
        )
        fast_strikers = await client.search_players(options=options)

        # Get Team of the Week
        totw = await client.get_totw()

        # Get latest players
        latest = await client.get_latest_players()

        # Get all leagues and clubs
        leagues = await client.get_leagues_and_clubs()

        # Get card versions (TOTW, TOTY, Icons, etc.)
        versions = await client.get_card_versions()

        # Use nations data
        nation = get_nation_name(54)  # Returns "Ethiopia"

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

### Nations Data

```python
from futbin_sdk import NATIONS, get_nation_name, get_nation_id

# Get nation name by ID
name = get_nation_name(22)  # Returns "Brazil"

# Get nation ID by name
nation_id = get_nation_id("Brazil")  # Returns 22

# Access full nations dictionary
print(NATIONS[22])  # "Brazil"
```

### Search Options

`PlayerSearchOptions` supports **40+ detailed attributes** for filtering players:

#### Basic Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | str | Platform: "PS" or "PC" |
| `page` | int | Page number (default: 1) |
| `sort` | str | Sort field |
| `order` | str | Sort order ("asc" or "desc") |
| `version` | str | Card version filter |
| `position` | list[str] | Position filter (e.g., ["ST", "CF"]) |
| `nation_id` | int | Nation ID filter |
| `league_id` | int | League ID filter |
| `club_id` | int | Club ID filter |

#### Rating & Price

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_rating` / `max_rating` | int | Rating range |
| `min_price` / `max_price` | int | Price range |

#### Skills & Physical

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_skills` / `max_skills` | int | Skill moves (1-5) |
| `min_weak_foot` / `max_weak_foot` | int | Weak foot (1-5) |
| `foot` | Foot | Preferred foot (LEFT/RIGHT) |
| `min_height` / `max_height` | int | Height in cm |
| `min_weight` / `max_weight` | int | Weight in kg |

#### Six Main Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_pace` / `max_pace` | int | Pace |
| `min_shooting` / `max_shooting` | int | Shooting |
| `min_passing` / `max_passing` | int | Passing |
| `min_dribbling` / `max_dribbling` | int | Dribbling |
| `min_defending` / `max_defending` | int | Defending |
| `min_physical` / `max_physical` | int | Physical |

#### Detailed Pace Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_acceleration` / `max_acceleration` | int | Acceleration |
| `min_sprint_speed` / `max_sprint_speed` | int | Sprint Speed |

#### Detailed Shooting Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_positioning` / `max_positioning` | int | Positioning |
| `min_finishing` / `max_finishing` | int | Finishing |
| `min_shot_power` / `max_shot_power` | int | Shot Power |
| `min_long_shots` / `max_long_shots` | int | Long Shots |
| `min_volleys` / `max_volleys` | int | Volleys |
| `min_penalties` / `max_penalties` | int | Penalties |

#### Detailed Passing Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_vision` / `max_vision` | int | Vision |
| `min_crossing` / `max_crossing` | int | Crossing |
| `min_free_kick` / `max_free_kick` | int | Free Kick Accuracy |
| `min_short_passing` / `max_short_passing` | int | Short Passing |
| `min_long_passing` / `max_long_passing` | int | Long Passing |
| `min_curve` / `max_curve` | int | Curve |

#### Detailed Dribbling Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_agility` / `max_agility` | int | Agility |
| `min_balance` / `max_balance` | int | Balance |
| `min_reactions` / `max_reactions` | int | Reactions |
| `min_ball_control` / `max_ball_control` | int | Ball Control |
| `min_composure` / `max_composure` | int | Composure |

#### Detailed Defending Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_interceptions` / `max_interceptions` | int | Interceptions |
| `min_heading_accuracy` / `max_heading_accuracy` | int | Heading Accuracy |
| `min_marking` / `max_marking` | int | Marking |
| `min_standing_tackle` / `max_standing_tackle` | int | Standing Tackle |
| `min_sliding_tackle` / `max_sliding_tackle` | int | Sliding Tackle |

#### Detailed Physical Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_jumping` / `max_jumping` | int | Jumping |
| `min_stamina` / `max_stamina` | int | Stamina |
| `min_strength` / `max_strength` | int | Strength |
| `min_aggression` / `max_aggression` | int | Aggression |

#### Goalkeeper Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_gk_diving` / `max_gk_diving` | int | GK Diving |
| `min_gk_handling` / `max_gk_handling` | int | GK Handling |
| `min_gk_kicking` / `max_gk_kicking` | int | GK Kicking |
| `min_gk_positioning` / `max_gk_positioning` | int | GK Positioning |
| `min_gk_reflexes` / `max_gk_reflexes` | int | GK Reflexes |

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
| `Foot` | Foot enum (LEFT, RIGHT) |

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
| 40+ search attributes | ✅ | ✅ | ❌ |
| Popular players | ✅ | ✅ | ❌ |
| TOTW players | ✅ | ✅ | ❌ |
| Latest players | ✅ | ✅ | ❌ |
| Leagues & Clubs | ✅ | ✅ | ❌ |
| Card versions | ✅ | ✅ | ❌ |
| Nations data | ✅ | ✅ | ❌ |
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
