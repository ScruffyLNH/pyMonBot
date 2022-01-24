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

    @commands.command()
    async def getUserId(self, ctx):
        """Get the discord id for the author of the command message.
        """
        await ctx.send(f'Your user ID is: {ctx.author.id}')

    @commands.command()
    async def getChannelId(self, ctx):
        """Get the channel id of the channel where command was invoked.
        """
        await ctx.send(f'This channels ID is: {ctx.channel.id}')

    @commands.command()
    async def getServerId(self, ctx):
        """Get the server id of the server where command was invoked.
        """
        await ctx.send(f'This server\'s ID is: {ctx.guild.id}')

    @commands.command()
    async def clear(self, ctx, amount=1):
        """Clear message(s) in a channel.

        :param amount: Amount of messages to delete, defaults to 1
        :type amount: int, optional
        """
        await ctx.channel.purge(limit=(amount + 1))

    @commands.command()
    async def findUser(self, ctx, user):
        """Searches for a user within the server where command was invoked and 
        displays the user ID if a close match is found.

        Args:
            userName (string): Name or nickname of the user to be found.
        """

        nameRatios = [
            lev.ratio(user, u.name) for u in ctx.guild.members]
        bestNameMatch = max(nameRatios)

        nickRatios = [
            lev.ratio(user, u.display_name) for u in ctx.guild.members]
        bestNickMatch = max(nickRatios)

        if bestNameMatch >= bestNickMatch:
            bestMatch = bestNameMatch
            index = nameRatios.index(bestNameMatch)
        else:
            bestMatch = bestNickMatch
            index = nickRatios.index(bestNickMatch)

        if bestMatch >= self.bot.config.reqMatchRatio:
            member = ctx.guild.members[index]
            await ctx.send(f'Best match is {member.name}, ID: {member.id}')
        else:
            await ctx.send('Unable to find matching user.')
    
    # Command check for entire cog. Invoker is admin.
    def cog_check(self, ctx):
        return (ctx.author.id == self.bot.config.adminId)

def setup(bot):
    bot.add_cog(DevTools(bot))