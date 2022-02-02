from pydantic import BaseModel
from decimal import Decimal
from typing import List

class Configuration(BaseModel):

    lfServerId: int = None # Id of the Legacy Fleet server
    adminId: int = 312381318891700224 # Scruffy_90
    superUsers: List[int] = [] # Users with elevated permissions
    contributerVoiceCategoryName: str = None # The category from wich to pull participants from all VCs.
    serviceCharge: Decimal = 0.005 # Service charge for transactions in the MO.Trader
    reqMatchRatio: float = 0.7 # A float between 0 and 1 determining matching strictness.