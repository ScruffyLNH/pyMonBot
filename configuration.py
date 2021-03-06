from pydantic import BaseModel
from decimal import Decimal

class Configuration(BaseModel):

    LfServerId: int = None # Id of the Legacy Fleet server
    adminId: int = 312381318891700224 # Scruffy_90
    contributerVoiceCategoryName: str = None # The category from wich to pull participants from all VCs.
    serviceCharge: Decimal = 0.005 # Service charge for transactions in the MO.Trader
