from discord import SlashOption
import nextcord # noqa
import Levenshtein as lev # Used for fuzzy string matching.
from nextcord import Interaction
from utility import sendMessagePackets, saveData
from constants import Constants
from nextcord.ext import commands

class DevTools(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='ping',
        description='Verify bot is online.',
        force_global=False, # TODO: Figure out how to set this across cogs.
    )
    async def sPing(self, inter: Interaction):
        await inter.response.send_message('Pong!')

    # Commands
    @commands.command()
    async def ping(self, ctx):
        """Verify bot is online. Bot should respond with "Pong!"
        """
        await ctx.send('Pong!')

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='get_user_id',
        description='Get the ID of the user invoking command.',
        force_global=False,
    )
    async def sGetUserId(self, inter: Interaction):

        userId = inter.user.id
        msg = f'Your user ID is: {userId}'
        await inter.response.send_message(msg)

    @commands.command()
    async def getUserId(self, ctx):
        """Get the discord id for the author of the command message.
        """
        await ctx.send(f'Your user ID is: {ctx.author.id}')

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='get_channel_id',
        description='Get the id of this channel.',
        force_global=False,
    )
    async def sGetChannelId(self, inter: Interaction):

        channelId = inter.channel.id
        msg = f'This channel\'s ID is: {channelId}'
        await inter.response.send_message(msg)

    @commands.command()
    async def getChannelId(self, ctx):
        """Get the channel id of the channel where command was invoked.
        """

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='get_server_id',
        description='Get the id of this server.',
        force_global=False,
    )
    async def sGetServerId(self, inter: Interaction):

        serverId = inter.guild.id
        msg = f'The ID of this server is: {serverId}'
        inter.response.send_message(msg)


    @commands.command()
    async def getServerId(self, ctx):
        """Get the server id of the server where command was invoked.
        """
        await ctx.send(f'This server\'s ID is: {ctx.guild.id}')

    @nextcord.slash_command(
        guild_ids=Constants.TEST_SERVER_IDS,
        name='clear',
        description='Clear message(s) in current channel.',
        force_global=False,
    )
    async def sClear(
        self,
        inter: Interaction,
        n: int = SlashOption(
            name='n',
            description='Number of messages.',
            default=1,
            min_value=1,
            required=False,
        )
    ):
        await inter.response.send_message('clearing')
        await inter.channel.purge(limit=(n + 1))


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