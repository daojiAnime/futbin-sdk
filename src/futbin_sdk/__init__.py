"""FUTBIN SDK - Python client for FUTBIN API

Unofficial SDK for accessing FIFA Ultimate Team player prices and statistics from FUTBIN.
"""

from futbin_sdk.client import FutbinClient
from futbin_sdk.models import CardVersion, Platform, Player, PlayerPrice

__version__ = "0.1.0"
__all__ = ["FutbinClient", "Player", "PlayerPrice", "Platform", "CardVersion"]
