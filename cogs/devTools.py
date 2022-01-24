import discord # noqa
import Levenshtein as lev # Used for fuzzy string matching.
from utility import sendMessagePackets, saveData
from constants import Constants
from discord.ext import commands

class DevTools(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command()
    async def ping(self, ctx):
        """Verify bot is online. Bot should respond with "Pong!"
        """
        await ctx.send('Pong!')