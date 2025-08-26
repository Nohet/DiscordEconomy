from typing import List
from dataclasses import dataclass


@dataclass
class Item:
    id: int
    name: str
    owner_id: int


@dataclass
class User:
    """
    User object, returned from a database.
    """
    id: int
    bank: float
    wallet: float
    items: List[Item]
