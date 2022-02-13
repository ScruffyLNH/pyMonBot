import nextcord # noqa
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

    def makePayoutEmbed(ctx, contribution, settings, authorDivvy):
        """Generates an embed for making payments when a contribution is made.

        Args:
            ctx (context): Either nextcord.ext.commands.contex or nextcord.interaction
            payments (Dict): [description]
            settings (Dict): Various settings contribution settings to be shown
            in the embed.

        Returns:
            nextcord.Embed, nextcord.File : Embed and file to be used in a
            nextcord.abc.Messageble.send()
        """

        # TODO: Deal with ctx / interaction
        if isinstance(ctx, nextcord.Interaction):
            author = ctx.user
        else:
            author = ctx.author

        # TODO: Add logic to only deal with 20 users at a time.
        f = nextcord.File('img/LF_emblem_lo_res.png', filename='LF_emblem_lo_res.png')
        e = nextcord.Embed(
            title=contribution.eventName,
            color=Constants.BOT_COLOR,
        )

        table = tt.Texttable(max_width=49)
        table.header(["","#","Handle","Amount","Mltp"])
        for i, payout in enumerate(contribution.payouts):
            table.add_row(
                [
                    '[]',
                    str(i + 1),
                    payout.outstanding['name'],
                    round(payout.outstanding['amount']),
                    payout.outstanding['multiplier'],
            ]
            )
        tableStr = '```\n'+table.draw()+'\n```'
        descriptionStr = (
            f'Sharing **{contribution.amount} {contribution.assetType.name}**'
        )
        
        if settings['equal']:
            descriptionStr += ' equally.'
        else:
            descriptionStr += ' according to multipliers.'
        descriptionStr += (
            f'\n{authorDivvy[1]}\'s share is '
            f'{round(authorDivvy[0])} {contribution.assetType.name}'
        )
        
        descriptionStr += (
            f'\nIn game transaction fee is {str(float(settings["fee"]*100))}%'
        )
        descriptionStr += '\n\n'
        descriptionStr += '```\n'+table.draw()+'\n```'
        
        e.description=(
            descriptionStr
        )
        # e.description=(table.draw())

        # TODO: Figure out reaction emojis and how to deal with payed/unpayed users.
        
        numStr = nameStr = amountStr = multStr = ''
        for payout in contribution.payouts:
            numStr += (
                ':one:' # Hmm do I use dict or enum?
            )
            nameStr += (
                f'\n~~{payout.outstanding["name"]}~~'
            )
            amountStr += (
                f'\n~~{round(payout.outstanding["amount"])}~~'
            )
            multStr += (
                f'\n{payout.outstanding["multiplier"]}'
            )

        e.set_thumbnail(url='attachment://LF_emblem_lo_res.png')
        #e.set_thumbnail(url=Constants.THUMBNAIL_URL)

        # TODO: Dry this.
        if ctx.guild.icon:
            e.set_footer(
                text='Helpful hints in footer maybe?',
                icon_url=ctx.guild.icon.url,
            )
        else:
            e.set_footer(text='Helpful hints in footer maybe?')

        return e, f