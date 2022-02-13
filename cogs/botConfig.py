import nextcord # noqa
from nextcord import Interaction, SlashOption
import asyncio
from configuration import Event
import discordParser
from datetime import datetime, timezone
from nextcord.ext import commands
from utility import saveData
from constants import Constants
import logging
import pytz

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dtFormat = '%m:%d:%y:%H'
        self.dtHumanFormat = '%A, %b %d, %Y @%H:00 UTC'

    
    # TODO: Dry wet code (slash command copies regular commands.)
    # Slash Commands
    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='add_superuser',
        description='Add a superuser from members of server.',
        force_global=False,
    )
    async def sAddSuperUser(
        self,
        inter: Interaction,
        user: str = SlashOption(
            name='user',
            description='Users server nick, or name if none exists.',
        ),
    ):
        
        # user comes from subcommand (autocomplete)
        try:
            userId = int(user)
        except ValueError:
            await inter.response.send_message(
                'Unable to process command.\n' 
                'Please make sure to use one of the suggested options.',
                ephemeral=True,
            )
            return

        m = inter.guild.get_member(userId)
        if userId not in self.bot.config.superUsers:
            self.bot.config.superUsers.append(userId)    
            configData = self.bot.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)
            await inter.response.send_message(
                f'Added {m.display_name} with ID: {user} to super users.',
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                f'{m.display_name} is already a super user.',
                ephemeral=True,
            )

    @sAddSuperUser.on_autocomplete('user')
    async def subcommand(self, inter: Interaction, user: str):
        # Get all users in guild. (No bots)
        allUsers = [u for u in inter.guild.members if u.bot==False]
        # Convert to dictionary with names: id as key value pairs.
        allNames = dict([(n.display_name, str(n.id)) for n in allUsers])
        if not user:
            await inter.response.send_autocomplete(allNames)
            return
        userMatching = discordParser.fuzzyMatcher(allUsers, user)
        await inter.response.send_autocomplete(userMatching)

    
    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='remove_superuser',
        description='Remove a user as super user.',
        force_global=False,
    )
    async def sRemoveSuperUser(
        self,
        inter: Interaction,
        user: str = SlashOption(
            name='user',
            description='The user to remove from super users.',
        ),
    ):
        
        try:
            userId = int(user)
        except ValueError:
            await inter.response.send_message(
                'Unable to process command.\n'
                'Please make sure to use one of the suggested options.',
                ephemeral=True,
            )
            return

        u = inter.guild.get_member(userId)
        if userId in self.bot.config.superUsers:
            self.bot.config.superUsers.remove(userId)
            configData = self.bot.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)
            await inter.response.send_message(
                f'Removed {u.display_name} with ID: {user} from super users.',
                ephemeral=True
            )
        else:
            await inter.response.send_message(
                f'User {u.display_name} not found in super users.',
                ephemeral=True
            )
            logger = logging.getLogger('nextcord')
            logger.warning(
                'Unable to find super user when trying to remove.'
            )


    @sRemoveSuperUser.on_autocomplete('user')
    async def subcommand(self, inter: Interaction, user: str):
        
        # Check that all super users are visible to the bot.
        sUsers = []
        for id in self.bot.config.superUsers:
            u = self.bot.get_user(id)
            if u:
                sUsers.append(u)
            try:
                assert u is not None
            except AssertionError:
                logger = logging.getLogger('nextcord')
                logger.warning(
                    'Superuser not visible to bot.\n'
                    'Invalid id, removing'
                )
                self.bot.config.superUser.remove(id)
        userNames = dict([(u.display_name, str(u.id))for u in sUsers])
        if not user:
            await inter.response.send_autocomplete(userNames)
            return
        userMatching = discordParser.fuzzyMatcher(sUsers, user)
        await inter.response.send_autocomplete(userMatching)

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='view_superusers',
        description='View people with elevated priviliges.',
        force_global=False,
    )
    async def sViewSuperUsers(self, inter: Interaction):

        msg = "The following users have superuser priviliges: \n\n"

        if self.bot.config.superUsers:
            for id in self.bot.config.superUsers:
                user = self.bot.get_user(id)
                msg += f'{user.name}, ID: {id}\n'
            await inter.response.send_message(msg, ephemeral=True)
        else:
            await inter.response.send_message(
                'No superusers were found.',
                ephemeral=True,
            )

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='set_event_name',
        description=
            'Set event name. Only use if event is taking place in the '
            'Legacy Fleet server.',
        force_global=False,        
    )
    async def sSetEventName(
        self,
        inter: Interaction,
        eventName: str = SlashOption(
            name='event_name',
            description='Name of the event.',
        ),
        duration: int = SlashOption(
            name='event_duration',
            description='expected duration of the event in hours',
            default=12,
            min_value=1,
            required=False,
        ),
        startDate: str = SlashOption(
            name='start_date',
            description=
            'The start date and time for the event. mm:dd:yy:HH:',
            required=False,
        )
    ):
        now = datetime.now(timezone.utc)
        if startDate:
 
            sd = datetime.strptime(startDate, self.dtFormat)
            awareSd = pytz.timezone('UTC').localize(sd)
            td = awareSd-now
            if td.days < 0:
                await inter.response.send_message(
                    'Start date should be later than now. '
                    'If event is ongoing don\'t set start date option.',
                    ephemeral=True
                )
                return
            hoursUntilEvent = td.seconds // 3600 + td.days * 24
            # TODO: Finish this slash command.
            


    @sSetEventName.on_autocomplete('startDate')
    async def subcommand(self, inter: Interaction, startDate: str):
        
        now = datetime.now(timezone.utc)
        rawStartDate = datetime.strftime(now, self.dtFormat)
        readableStartDate = datetime.strftime(now, self.dtHumanFormat)
        acDict = {readableStartDate + ' / ' + rawStartDate: rawStartDate}
        if not startDate:
            await inter.response.send_autocomplete(acDict)
            return
        else:
            #Substitute default startDate with user input
            newStartDate = startDate + rawStartDate[len(startDate):]
            try:
                newDateTime = datetime.strptime(newStartDate, self.dtFormat)
            except ValueError:
                # await inter.response.send_autocomplete({'?': '?'})
                return
            
            newRawStartDate = datetime.strftime(newDateTime, self.dtFormat)
            newReadableStartDate = datetime.strftime(
                newDateTime, self.dtHumanFormat
            )
            newAcDict = {newReadableStartDate + ' / ' + newRawStartDate:
            newRawStartDate}
            await inter.response.send_autocomplete(newAcDict)

    # Commands
    @commands.command(name='addSuperUser')
    async def addSuperUser(self, ctx, id):
        """Add superuser by passing users ID for elevated permissions

        Args:
            id (int): superuser ID
        """

        user = self.bot.get_user(int(id))
        if user:
            if int(id) not in self.bot.config.superUsers:
                await ctx.send(f'{user.name} has been added to superusers.')
                self.bot.config.superUsers.append(int(id))
                configData = self.bot.config.json(indent=2)
                saveData(Constants.CONFIG_DATA_FILENAME, configData)
            else:
                await ctx.send('User is already a superuser.')
        else:
            await ctx.send('Could not find any user with that ID.')

    @commands.command(name='removeSuperUser')
    async def removeSuperUser(self, ctx, id):
        """Remove superuser by passing the ID of the user to be removed.

        Args:
            id (int): superuser ID
        """

        user = self.bot.get_user(int(id))

        if user:
            try:
                self.bot.config.superUsers.remove(int(id))
                await ctx.send(
                    f'Successfully removed {user.name} as superuser.'
                )
                configData = self.bot.config.json(indent=2)
                saveData(Constants.CONFIG_DATA_FILENAME, configData)
            except ValueError:
                await ctx.send('User not found in superuser list.')
        else:
            await ctx.send('Could not find any user with that ID.')

    @commands.command(name='viewSuperUsers')
    async def viewSuperUsers(self, ctx):
        """View all people who has superuser priviliges.
        """

        superUsers = "The following users have superuser priviliges:\n\n"

        if self.bot.config.superUsers:
            for id in self.bot.config.superUsers:
                user = self.bot.get_user(id)
                superUsers += f'{user.name}, id: {id}\n'

            await ctx.send(superUsers)
        else:
            await ctx.send("No superusers were found.")

    @commands.command(name='setMatchRatio')
    async def setMatchRatio(self, ctx, ratio):
        """Set the matching ratio required to show enteties when using search
        commands.

        Args:
            ratio (float): Matching ratio. Must be able to be coerced to float.
        """
        errorMsg = 'Value must be a real number between 0 and 1'
        try:
            r = float(ratio)
            if r > 0 and r <= 1:
                self.bot.config.reqMatchRatio = r
                configData = self.bot.config.json(indent=2)
                saveData(Constants.CONFIG_DATA_FILENAME, configData)
                await ctx.send(f'Matching ratio has been set to {r}')
            else:
                await ctx.send(errorMsg)

        except ValueError:
            await ctx.send(errorMsg)
        except OverflowError:
            await ctx.send(errorMsg)

    @commands.command(name='setVoiceCategoryName')
    async def setVoiceCategoryName(self, ctx, *, categoryName=''):
        """Set the name of the voice category where bot will fetch users during
        an event.

        Args:
            categoryName (string): Name of the voice category.
        """
        cName = categoryName.upper()
        self.bot.config.contributerVoiceCategoryName = cName
        configData = self.bot.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)

        await ctx.send(f'Voice category name has been set to {cName}')

    @commands.command(name='setEventName')
    async def setEventName(self, ctx, *, eventName=''):
        """Set the name of the event. Only use if event is taking place in the
        Legacy Fleet server.

        Args:
            eventName (str): The name of the event.
        """
        if self.bot.config.userDefinedEvent:
            if self.bot.config.userDefinedEvent.name == eventName:
                # Extend lifetime of the user defined event.
                # TODO: Refactor this. Too convoluted.
                self.bot.config.userDefinedEvent = Event(
                    name=eventName,
                    id=self.bot.config.userDefinedEvent.id,
                    timeStamp=datetime.now(timezone.utc)
                )
                configData = self.bot.config.json(indent=2)
                saveData(Constants.CONFIG_DATA_FILENAME, configData)
                await ctx.send(f'"{eventName}" has been extended.')
                return

        newEvent = Event(
            name=eventName,
            id=nextcord.utils.time_snowflake(datetime.now()),
            # TODO: Test Event with timezone datetime
            timeStamp=datetime.now(timezone.utc)
        )
        self.bot.config.userDefinedEvent = newEvent

        configData = self.bot.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)

        await ctx.send(f'Event name has been set to "{eventName}"')


    @commands.command(name='runServerTest')
    async def runServerTest(self, ctx):
        """Run test to check roles and that bot can see the correct VCs.
        """

        # TODO: Add checking of roles to command.

        voiceChannels = discordParser.getVoiceChannelsByCategoryName(
            ctx,
            self.bot.config.contributerVoiceCategoryName,
        )
        if voiceChannels:
            voiceClient = ctx.guild.voice_client
            if voiceClient:
                await voiceClient.disconnect()
            for vc in voiceChannels:
                voiceClient = await vc.connect()
                await asyncio.sleep(0.8)
                await voiceClient.disconnect()
        else:
            await ctx.send('Unable to find needed catrgory channel.')

    # Command check for entire cog. Invoker is either admin or superuser.
    def cog_check(self, ctx):
        return (ctx.author.id == self.bot.config.adminId or 
        ctx.author.id in self.bot.config.superUsers)

def setup(bot):
    bot.add_cog(BotConfig(bot))