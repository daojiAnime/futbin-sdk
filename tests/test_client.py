"""Tests for FutbinClient"""

import pytest
from futbin_sdk import FutbinClient, Platform


@pytest.mark.asyncio
async def test_get_popular_players():
    """测试获取热门球员"""
    async with FutbinClient() as client:
        players = await client.get_popular_players()
        assert len(players) > 0
        assert players[0].futbin_id > 0


@pytest.mark.asyncio
async def test_get_player_price():
    """测试获取球员价格"""
    async with FutbinClient() as client:
        # 使用热门球员测试
        popular = await client.get_popular_players()
        if popular:
            player_id = popular[0].futbin_id
            price = await client.get_player_price(player_id, Platform.PS)
            assert price.price >= 0


@pytest.mark.asyncio
async def test_get_players_prices():
    """测试批量获取球员价格"""
    async with FutbinClient() as client:
        popular = await client.get_popular_players()
        if len(popular) >= 3:
            player_ids = [p.futbin_id for p in popular[:3]]
            prices = await client.get_players_prices(player_ids, Platform.PS)
            assert len(prices) == 3
