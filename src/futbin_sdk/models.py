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


class FullPlayer(BaseModel):
    """完整球员信息（来自搜索/TOTW/最新球员 API）"""

    futbin_id: int = Field(description="FUTBIN ID")
    player_id: int = Field(default=0, description="球员 ID")
    resource_id: int = Field(default=0, description="EA Resource ID")
    name: str = Field(default="", description="球员名称")
    common_name: str = Field(default="", description="常用名")
    rating: int = Field(default=0, description="评分")
    position: str = Field(default="", description="主位置")
    positions: str = Field(default="", description="所有位置")
    rare_type: int = Field(default=0, description="稀有类型")

    # 俱乐部/国家/联赛
    club_id: int = Field(default=0, description="俱乐部 ID")
    club: str = Field(default="", description="俱乐部名称")
    nation_id: int = Field(default=0, description="国家 ID")
    nation: str = Field(default="", description="国家名称")
    league_id: int = Field(default=0, description="联赛 ID")
    league: str = Field(default="", description="联赛名称")

    # 六边形属性
    pace: int = Field(default=0, description="速度")
    shooting: int = Field(default=0, description="射门")
    passing: int = Field(default=0, description="传球")
    dribbling: int = Field(default=0, description="盘带")
    defending: int = Field(default=0, description="防守")
    physical: int = Field(default=0, description="身体")

    # 价格信息
    price_ps: int = Field(default=0, description="PS 价格")
    price_pc: int = Field(default=0, description="PC 价格")
    price_xbox: int = Field(default=0, description="Xbox 价格")
    min_price_ps: int = Field(default=0, description="PS 最低价")
    max_price_ps: int = Field(default=0, description="PS 最高价")
    min_price_pc: int = Field(default=0, description="PC 最低价")
    max_price_pc: int = Field(default=0, description="PC 最高价")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "FullPlayer":
        """从 API 响应解析球员"""
        return cls(
            futbin_id=int(data.get("ID", 0)),
            player_id=int(data.get("playerid", 0)),
            resource_id=int(data.get("resource_id", 0)),
            name=data.get("playername", "") or data.get("name", ""),
            common_name=data.get("common_name", ""),
            rating=int(data.get("rating", 0)),
            position=data.get("position", ""),
            positions=data.get("pos_all", ""),
            rare_type=int(data.get("raretype", 0)),
            club_id=int(data.get("club", 0)),
            club=data.get("club_name", ""),
            nation_id=int(data.get("nation", 0)),
            nation=data.get("nation_name", ""),
            league_id=int(data.get("league", 0)),
            league=data.get("league_name", ""),
            pace=int(data.get("pac", 0)),
            shooting=int(data.get("sho", 0)),
            passing=int(data.get("pas", 0)),
            dribbling=int(data.get("dri", 0)),
            defending=int(data.get("def", 0)),
            physical=int(data.get("phy", 0)),
            price_ps=int(data.get("ps_LCPrice", 0) or 0),
            price_pc=int(data.get("pc_LCPrice", 0) or 0),
            price_xbox=int(data.get("xbox_LCPrice", 0) or 0),
            min_price_ps=int(data.get("ps_MinPrice", 0) or 0),
            max_price_ps=int(data.get("ps_MaxPrice", 0) or 0),
            min_price_pc=int(data.get("pc_MinPrice", 0) or 0),
            max_price_pc=int(data.get("pc_MaxPrice", 0) or 0),
        )


class PlayerSearchOptions(BaseModel):
    """球员搜索选项"""

    platform: str = Field(default="PS", description="平台 (PS/PC)")
    page: int = Field(default=1, description="页码")
    version: str | None = Field(default=None, description="卡片版本")
    position: list[str] | None = Field(default=None, description="位置列表")
    nation_id: int | None = Field(default=None, description="国家 ID")
    league_id: int | None = Field(default=None, description="联赛 ID")
    club_id: int | None = Field(default=None, description="俱乐部 ID")
    min_rating: int | None = Field(default=None, description="最低评分")
    max_rating: int | None = Field(default=None, description="最高评分")
    min_price: int | None = Field(default=None, description="最低价格")
    max_price: int | None = Field(default=None, description="最高价格")

    def to_params(self) -> dict[str, str | int]:
        """转换为 API 参数"""
        params: dict[str, str | int] = {
            "platform": self.platform,
            "page": self.page,
        }
        if self.version:
            params["version"] = self.version
        if self.position:
            params["position"] = ",".join(self.position)
        if self.nation_id:
            params["nation"] = self.nation_id
        if self.league_id:
            params["league"] = self.league_id
        if self.club_id:
            params["club"] = self.club_id
        if self.min_rating:
            params["rating_min"] = self.min_rating
        if self.max_rating:
            params["rating_max"] = self.max_rating
        if self.min_price:
            params["price_min"] = self.min_price
        if self.max_price:
            params["price_max"] = self.max_price
        return params


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


class League(BaseModel):
    """联赛信息"""

    league_id: int = Field(description="联赛 ID")
    name: str = Field(default="", description="联赛名称")
    clubs: list["Club"] = Field(default_factory=list, description="俱乐部列表")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "League":
        """从 API 响应解析联赛"""
        clubs = [Club.from_api_response(c) for c in data.get("clubs", [])]
        return cls(
            league_id=int(data.get("league_id", 0)),
            name=data.get("league_name", ""),
            clubs=clubs,
        )


class Club(BaseModel):
    """俱乐部信息"""

    club_id: int = Field(description="俱乐部 ID")
    name: str = Field(default="", description="俱乐部名称")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Club":
        """从 API 响应解析俱乐部"""
        return cls(
            club_id=int(data.get("club_id", 0)),
            name=data.get("club_name", ""),
        )


class CardVersionInfo(BaseModel):
    """卡片版本信息"""

    name: str = Field(default="", description="版本名称")
    key: str = Field(default="", description="版本键名")
    img: str = Field(default="", description="图片标识")

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "CardVersionInfo":
        """从 API 响应解析卡片版本"""
        return cls(
            name=data.get("version_name", ""),
            key=data.get("get", ""),
            img=data.get("img", ""),
        )


# 位置常量
class Position(StrEnum):
    """球员位置"""

    GK = "GK"
    RB = "RB"
    RWB = "RWB"
    LB = "LB"
    LWB = "LWB"
    CB = "CB"
    CDM = "CDM"
    CM = "CM"
    CAM = "CAM"
    RM = "RM"
    RW = "RW"
    RF = "RF"
    LM = "LM"
    LW = "LW"
    LF = "LF"
    CF = "CF"
    ST = "ST"
