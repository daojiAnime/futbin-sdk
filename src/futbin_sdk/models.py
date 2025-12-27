"""Data models for FUTBIN SDK"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Platform(StrEnum):
    """游戏平台"""

    PS = "PS"
    PC = "PC"
    XBOX = "XB"  # Xbox 与 PS 共享市场


class CardVersion(StrEnum):
    """卡片版本"""

    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    RARE = "rare"
    NON_RARE = "non_rare"
    TOTW = "totw"
    TOTY = "toty"
    TOTS = "tots"
    ICON = "icon"
    HERO = "hero"


class PlayerPrice(BaseModel):
    """球员价格信息"""

    price: int = Field(default=0, description="当前价格")
    min_price: int = Field(default=0, description="最低价格")
    max_price: int = Field(default=0, description="最高价格")
    updated: str = Field(default="", description="更新时间")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "PlayerPrice":
        """从 API 响应解析价格"""
        return cls(
            price=int(data.get("LCPrice", 0) or 0),
            min_price=int(data.get("MinPrice", 0) or 0),
            max_price=int(data.get("MaxPrice", 0) or 0),
            updated=str(data.get("updated", "")),
        )


class Player(BaseModel):
    """球员信息"""

    futbin_id: int = Field(description="FUTBIN ID")
    resource_id: int = Field(default=0, description="EA Resource ID")
    name: str = Field(default="", description="球员名称")
    rating: int = Field(default=0, description="评分")
    position: str = Field(default="", description="位置")
    club: str = Field(default="", description="俱乐部")
    league: str = Field(default="", description="联赛")
    nation: str = Field(default="", description="国籍")

    # 价格信息
    price_ps: PlayerPrice | None = Field(default=None, description="PS 平台价格")
    price_pc: PlayerPrice | None = Field(default=None, description="PC 平台价格")

    # 属性
    pace: int = Field(default=0, description="速度")
    shooting: int = Field(default=0, description="射门")
    passing: int = Field(default=0, description="传球")
    dribbling: int = Field(default=0, description="盘带")
    defending: int = Field(default=0, description="防守")
    physical: int = Field(default=0, description="身体")


class PopularPlayer(BaseModel):
    """热门球员"""

    futbin_id: int = Field(description="FUTBIN ID")
    resource_id: int = Field(default=0, description="EA Resource ID")
    name: str = Field(default="", description="球员名称")
    rating: int = Field(default=0, description="评分")
    price_ps: int = Field(default=0, description="PS 价格")
    price_pc: int = Field(default=0, description="PC 价格")


class ChemistryStyle(BaseModel):
    """化学卡"""

    name: str = Field(description="化学卡名称")
    ea_id: int = Field(default=0, description="EA ID (cardsubtypeid)")
    price_ps: int = Field(default=0, description="PS 平台价格")
    price_pc: int = Field(default=0, description="PC 平台价格")
    min_price_ps: int = Field(default=0, description="PS 最低价")
    max_price_ps: int = Field(default=0, description="PS 最高价")
    min_price_pc: int = Field(default=0, description="PC 最低价")
    max_price_pc: int = Field(default=0, description="PC 最高价")
    boost: str = Field(default="", description="加成属性")
    preferred_positions: list[str] = Field(default_factory=list, description="适用位置")


class ManagerCard(BaseModel):
    """教练员卡"""

    nation: str = Field(description="国籍")
    nation_id: int = Field(default=0, description="国籍 ID")
    bronze_price_ps: int = Field(default=0, description="铜卡 PS 价格")
    bronze_price_pc: int = Field(default=0, description="铜卡 PC 价格")
    silver_price_ps: int = Field(default=0, description="银卡 PS 价格")
    silver_price_pc: int = Field(default=0, description="银卡 PC 价格")
    gold_price_ps: int = Field(default=0, description="金卡 PS 价格")
    gold_price_pc: int = Field(default=0, description="金卡 PC 价格")


class LeagueCard(BaseModel):
    """联赛卡"""

    name: str = Field(description="联赛名称")
    league_id: int = Field(default=0, description="联赛 ID")
    price_ps: int = Field(default=0, description="PS 价格")
    price_pc: int = Field(default=0, description="PC 价格")
