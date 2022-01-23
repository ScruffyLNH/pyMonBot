import discord # noqa
from discord.ext import commands
from utility import saveData
from constants import Constants

class botConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Commands
    @commands.command(name='addSuperUser')
    async def addSuperUser(self, ctx, id):
        """Add superuser by passing users ID for elevated permissions

        Args:
            id (int): superuser Id
        """

        user = self.bot.get_user(int(id))

        if user:
            await ctx.send(f'{user.name} has been added to super users.')
            self.bot.config.superUsers.append(int(id))
            configData = self.bot.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)
        else:
            await ctx.send('Could not find any user with that ID.')

    # Command check for entire cog. Invoker is either admin or super user.
    def cog_check(self, ctx):
        return (ctx.author.id == self.bot.config.adminId or 
        ctx.author.id in self.bot.config.superUsers)

def setup(bot):
    bot.add_cog(botConfig(bot))