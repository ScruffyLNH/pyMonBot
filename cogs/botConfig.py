import discord # noqa
import asyncio
from discord.ext import commands
from utility import saveData
from constants import Constants

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
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

    @commands.command(name='runServerTest')
    async def runServerTest(self, ctx):
        """Run test to check roles and that bot can see the correct VCs.
        """

        # TODO: Add checking of roles to command.

        categories = ctx.guild.categories
        categoryChannel = None
        for c in categories:
            if c.name.upper() == self.bot.config.contributerVoiceCategoryName:
                categoryChannel = c
                break
        
        if categoryChannel:
            # If exists get active voice connection on server and disconnect.
            voiceClient = ctx.guild.voice_client
            if voiceClient:
                await voiceClient.disconnect()
            for vc in categoryChannel.voice_channels:
                voiceClient = await vc.connect()
                await asyncio.sleep(0.8)
                await voiceClient.disconnect()
        else:
            await ctx.send('Unable to find needed category channel.')

    # Command check for entire cog. Invoker is either admin or superuser.
    def cog_check(self, ctx):
        return (ctx.author.id == self.bot.config.adminId or 
        ctx.author.id in self.bot.config.superUsers)

def setup(bot):
    bot.add_cog(BotConfig(bot))