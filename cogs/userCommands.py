from datetime import datetime, timezone, timedelta
import nextcord # noqa
import discordParser
import configuration
from nextcord.ext import commands
from utility import saveData
from constants import Constants
from ledger import AssetType, Contribution, Ledger
from decimal import Decimal, InvalidOperation
from nextcord.ext.commands import MissingRequiredArgument

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command(name='share')
    async def share(self, ctx, amount, equalOption=None):
        """Divvy up income.

        Args:
            amount (str): The amount to distribute. (Positive real number)
            equalOption (str): Pass "equal" as second argument for equal shares.
        """
        
        # Exception handling.
        if await self.valueNotRealPositive(ctx, amount):
            return

        if ctx.guild.id == self.bot.config.lfServerId:
            # If in lf server, event name must have been specified to be valid.
            if await self.eventInvalid(self.bot, ctx):
                return
        
        if await self.voiceCategoryNameNotSet(ctx):
            return

        # TODO: Make voiceCategoryNotFound
        # if await self.voiceCategoryNotFound(ctx)
        #    return

        a = Decimal(amount)

        # Get all applicable users (No bots, not self)
        users = discordParser.getShareholders(self.bot, ctx)

        # Parse share roles
        shareUsers = discordParser.parseUsersWithShares(ctx)
        # Group users according to tier level in a dict.
        # If users have more than one share role only the highest role will be
        # counted.

        # TODO: Refactor move to separate methods.
        keys = sorted(shareUsers, reverse=True)
        aggregate = set()
        authorShare = None
        for myKey in keys:
            mySet = set(shareUsers[myKey])
            shareUsers[myKey] = list(mySet - aggregate)
            aggregate |= mySet
            if ctx.author in shareUsers[myKey]:
                authorShare = {myKey: ctx.author}

        if not authorShare:
            authorShare = {Decimal(1.0): ctx.author}
        # Filter shareUsers based on users present in VC
        agg = set()
        for mKey in keys:
            mSet = set(shareUsers[mKey])
            something = set(users).intersection(mSet)
            agg |= something
            shareUsers[mKey] = list(something)
        leftOvers = list(set(users) - agg)
        # Check if value 1.0 exists
        v = Decimal(1.0)
        if v in shareUsers:
            shareUsers[v] += leftOvers
        else:
            shareUsers[v] = leftOvers

        #print(authorShare)
        shareValue = self.calculateShareValue(a, shareUsers, authorShare)

        equal = False
        if equalOption:
            if equalOption.upper() == 'EQUAL':
                await ctx.send('Equal option selected.')
                equal = True

        finalDivvy = self.distributeShares(
            shareValue,
            shareUsers,
            equalShare=equal,
        )

        # TODO: Deal with rounding.

        # TODO: When adding reactions only let the command invoker click.

        # TODO: Make sure share embed displays equal/weighted shares.

        if ctx.guild.id == self.bot.config.lfServerId:
            eventId = self.bot.config.userDefinedEvent.id
            eventName = self.bot.config.userDefinedEvent.name
        else:
            eventId = ctx.guild.id
            eventName = ctx.guild.name


        c = Contribution(
            contributerId=ctx.author.id,
            eventId=eventId,
            eventName=eventName,
            assetType=AssetType.aUec,
            amount=a,
            timeStamp=datetime.now(timezone.utc),
        )

        # Make a nice embed.
        await ctx.send(embed=Ledger.makeEmbed(ctx))

        # Use markdown to strikethrough payments made.

    async def valueNotRealPositive(self, ctx, value):
        v = -1
        try:
            v = Decimal(value)
        except ValueError:
            await ctx.send('Value is not a number')
            return True
        except InvalidOperation:
            await ctx.send('Value is not a number')
            return True
        if v <= 0:
            await ctx.send('Value is not a positive number.')
            return True
        return False

    async def eventInvalid(self, bot, ctx):

        if not self.bot.config.userDefinedEvent:
            #eventInvalid = True
            mentions = discordParser.getSuperUserMentions(self.bot, ctx)
            await ctx.send(
                'Event name not found. This is required.\n'
                'Setting event name requires elevated access.\n'
                'Please specify event name.' + mentions + '\n'
                'Use !help to see list of available commands.'
            )
            return True

        now = datetime.now(timezone.utc)
        then = self.bot.config.userDefinedEvent.timeStamp
        delta = now - then
        if delta > timedelta(hours=12):
            #eventInvalid = True
            mentions = discordParser.getSuperUserMentions(self.bot, ctx)
            await ctx.send(
                f'Event name has expired. Valid event name is required.\n'
                f'To extend or set new event name requires elevated access.\n'
                f'Please specify event name. ' + mentions + '\n'
                f'To extend an ongoing event set the event name to the same as'
                f' it was. ("{self.bot.config.userDefinedEvent.name}")\n'
                f'Use !help to see list of available commands.'
            )
            return True

    async def voiceCategoryNameNotSet(self, ctx):
        if not self.bot.config.contributerVoiceCategoryName:
            mentions = discordParser.getSuperUserMentions(self.bot, ctx)
            await ctx.send(
                'Voice category name not specified.' + mentions
            )
            return True

    def calculateShareValue(self, amount, shareUsers, authorShare, calcFee=True):
        
        # Get all shares except for author
        allShares = Decimal(0)
        for shareMultiplyer in shareUsers:
            allShares += shareMultiplyer * Decimal(len(shareUsers[shareMultiplyer]))
        authorShareValue = next(iter(authorShare))

        if calcFee:
            fee = self.bot.config.serviceCharge
        else:
            fee = Decimal(0)
        
        shareValue = amount/(allShares*(1+fee)+authorShareValue)
        return shareValue


    # TODO: Refactor names.
    def distributeShares(self, shareValue, shareUsers, equalShare=False):
        finalDivvys = []
        for shareMultiplyer in shareUsers:
            if equalShare:
                divvy = shareValue
            else:
                divvy = shareMultiplyer * shareValue
            for user in shareUsers[shareMultiplyer]:
                finalDivvys.append((user,divvy))
        
        return finalDivvys

    # TODO: implement MissingRequiredArgument
    """
    @commands.Cog.listener
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("A parameter is missing") 
    """

def setup(bot):
    bot.add_cog(UserCommands(bot))