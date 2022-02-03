#from lib2to3.pytree import Base
import discord # noqa
from typing import List
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime
from constants import Constants

class AssetType(Enum):

    aUec = 1
    merits = 2

class Person(BaseModel):

    id: int
    name: str
    roles: List[str]


class ShareHolder(Person):

    moneyOwed: Decimal

class Contribution(BaseModel):
    
    contributerId: int = None
    eventId: int # eventId will usually be the server id # TODO: Figure out how to handle id's for events that last longer than the default 12h time.
    eventName: str
    assetType: AssetType
    amount: Decimal
    timeStamp: datetime
    messageId: int = None # Id for the message containing the payouts embed.
    paymentsOutstanding: List[ShareHolder] = [] # Payments outstanding will not mix between events.


class Ledger(BaseModel):

    contributions: List[Contribution] = []

    # Returns all contribution records and necessary associated data for user.
    def getUserRecord():
        pass
    
    # 
    def getSummary():
        pass

    def makeEmbed(ctx):
        # Users should contain payout amounts?
        e = discord.Embed(
            title='Event Name',
            description='~~something~~',
            color=Constants.BOT_COLOR,
        )
        
        e.set_thumbnail(url=Constants.THUMBNAIL_URL)
        
        e.set_footer(
            text='something',
            icon_url=ctx.guild.icon_url,
        )

        return e