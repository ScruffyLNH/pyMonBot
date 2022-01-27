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
    eventId: int = None # eventId will usually be the server id # TODO: Figure out how to handle id's for events that last longer than the default 12h time.
    messageId: int = None # Id for the message containing the payouts embed.
    eventName: str = None
    assetType: AssetType
    amount: Decimal
    timeStamp: datetime


class Ledger(BaseModel):

    contributions: List[Contribution] = []

    def getSummary(self):
        return None