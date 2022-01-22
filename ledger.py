#from lib2to3.pytree import Base
from typing import List
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class AssetType(Enum):

    aUec = 1
    merits = 2

class Contribution(BaseModel):
    
    contibuterId: int = None
    serverId: int = None
    serverName: str = None
    assetType: AssetType
    amount: Decimal
    timeStamp: datetime


class Ledger(BaseModel):

    contributions: List[Contribution] = []

    def getSummary(self):
        return None