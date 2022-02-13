from datetime import datetime, timezone, timedelta
import nextcord # noqa
import discordParser
import configuration
import ledger
from nextcord.ext import commands
from utility import saveData
from constants import Constants
from decimal import Decimal, InvalidOperation
from nextcord.ext.commands import MissingRequiredArgument

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # Slash commands
    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='share',
        description='Share income among users in applicable voice chats.',
        force_global=False,
    )
    async def sShare(
        self,
        inter: Interaction,
        amount: int = SlashOption(
            name='amount',
            description='The amount to be shared.',
            min_value=1,
        ),
        equal: bool = SlashOption(
            name='equal_share',
            description=
            'Whether or not to share equally or based on \"rank\" '
            'Default: False',
            default=False,
            required=False,
        ),
        transactionFee: float = SlashOption(
            name='transaction_fee',
            description= # TODO: Figure out how to update from self.bot.config
            f'In-game transaction fee. Defaults to 0.005 (0.5%)',
            default=0.005,
            required=False,
            min_value=float(0),
        ),
        logContribution: bool = SlashOption(
            name='log_contribution',
            description=
            'Whether or not to save the contribution in ledger. Default: True '
            '(use False for testing.)',
            default=True,
            required=False,
        ),
    ):
        author = inter.user
        transactionFee = Decimal(transactionFee)

        if inter.guild.id == self.bot.config.lfServerId:
            eventId = self.bot.config.userDefinedEvent.id
            eventName = self.bot.config.userDefinedEvent.name
        else:
            eventId = inter.guild.id
            eventName = inter.guild.name

        if inter.guild.id == self.bot.config.lfServerId:
            if await self.eventInvalid(self.bot, inter):
                return
        
        if await self.voiceCategoryNameNotSet(inter):
            return
            
        # TODO: Make voiceCategoryNotFound Check

        # Get all applicable users (No bots, not self)
        usersInVoice = discordParser.getUsersInVc(self.bot, inter)
        if await self.noUsersInVc(inter, len(usersInVoice)):
            return

        # Parse share roles
        shareUsers = discordParser.parseUsersWithShares(inter)

        # Reorder shareusers according to share multiplier, and make sure
        # shareholders are not duplicated into lower multipliers if they have
        # more than one share multiplier role.
        shareUsers, authorShare = discordParser.arrangeShareUsers(
            author,
            shareUsers,
        )

        # Filter shareUsers based on users present in VC
        shareUsers = discordParser.filterVoiceConnected(
            shareUsers,
            usersInVoice,
        )

        shareValue = self.calculateShareValue(
            Decimal(amount),
            shareUsers,
            authorShare,
            fee=transactionFee,
            equalOption=equal,
        )

        finalDivvys = self.distributeShares(
            shareValue,
            shareUsers,
            equalShare=equal,
        )

        payouts = []
        for d in finalDivvys:
            user, divvy, mp = d
            p = ledger.Payout(
                outstanding={
                    'id': user.id,
                    'name': user.display_name,
                    'amount': divvy,
                    'multiplier': mp
                }
            )
            payouts.append(p)
        
        c = ledger.Contribution(
            contributerId=author.id,
            eventId=eventId,
            eventName=eventName,
            assetType=ledger.AssetType.aUec, # TODO: Implement option in slash command.
            amount=amount,
            payouts=payouts,
            timeStamp=datetime.now(timezone.utc)
        )
        if equal:
            authorDivvy = (shareValue, author.name)
        else:
            authorDivvy = (shareValue * next(iter(authorShare)), author.name)
        settings = {'equal': equal, 'fee': transactionFee}

        # TODO: Add what comd invoker is left with and what goes to trns-act-fee
        # Make a nice embed.
        e, f = ledger.Ledger.makePayoutEmbed(inter, c, settings, authorDivvy)
        # view = ViewClassName()
        msg = await inter.response.send_message(embed=e, file=f,)#view=view )
        #c.messageId = msg.id # TODO: Hmm this is odd. Check how to track interaction msg
        # await view.wait()
        # TODO: serialize contribution instance.


    async def noUsersInVc(self, ctx, numUsers):
        
        # TODO: DRY slash command check, maybe make a decorator?
        if isinstance(ctx, nextcord.Interaction):
            slashCommand = True
        else:
            slashCommand = False

        if numUsers < 1:
            noUsrStr = (
                'No users found in voice chat. Make sure at least one '
                'user other than command invoker is in voice and check '
                'voice category name in config.'
            )
            deleteTime = 15.0
            if slashCommand:
                await ctx.response.send_message(
                    noUsrStr,
                    delete_after=deleteTime
                )
            else:
                await ctx.send(
                    noUsrStr,
                    delete_after=deleteTime
                )
            return True


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

        slashCommand = False
        if isinstance(ctx, nextcord.Interaction):
            slashCommand = True
        if not self.bot.config.userDefinedEvent:
            #eventInvalid = True
            mentions = discordParser.getSuperUserMentions(self.bot, ctx)
            msg = (
                'Event name not found. This is required.\n'
                'Setting event name requires elevated access.\n'
                'Please specify event name.' + mentions + '\n'
            )
            if slashCommand:
                await ctx.response.send_message(msg)
            else:
                await ctx.send(msg)
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