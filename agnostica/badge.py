from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .asset import Asset

class Badge:
    """Represents a badge on a platform"""
    __slots__: Tuple[str, ...] = (
        "id",
        "name",
        "asset",
        "amount"
    )

    def __init__(self, id: str, name: str, asset: Optional[Asset], amount: Optional[int]):
        self.id = id
        self.name = name
        self.asset = asset
        self.amount = amount or 1
    
    def __repr__(self):
        return f"<Badge id={self.id} name={self.name} amount={self.amount}>"
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other: Any):
        if type(other) != Badge:
            return False
        else:
            return self.id == other.id and self.amount == other.amount
    
    def __hash__(self):
        return hash((self.id, self.amount))