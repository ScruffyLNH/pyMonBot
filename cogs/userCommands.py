import discord # noqa
import discordParser
from discord.ext import commands
from utility import saveData
from constants import Constants
from ledger import Ledger
from decimal import Decimal, InvalidOperation

class UserCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command(name='share')
    async def share(self, ctx, amount, equalOption=None):
        """Divvy up income.

        Args:
            amount (decimal): The amount to distribute. (Positive real number)
            equalOption (str): Pass "equal" as second argument for equal shares.
        """
        
        errorMsg = "Enter a real positive number."
        try:
            a = Decimal(amount)
            if a > 0:
                # TODO: Finish command.
                #
                # Get all applicable users (No bots, not self)
                users = discordParser.getShareholders(self.bot, ctx,)

                # Group users according to tier level.
                # Calculate adjusted service charge (user share not subject to service charge)
                # 1 - user weight divide by all users multiplied by their weight 
                # netAmount = a * adjustedServiceCharge
                # divide net amount among users.

                # TODO: Deal with rounding.

                # TODO: When adding reactions only let the command invoker click.


                # Check if user wants to share equally in group.
                equal = False
                if equalOption:
                    if equalOption.upper() == 'EQUAL':
                        await ctx.send('Equal option selected.')
                        equal = True
                # Continue code here.

                # Make a nice embed.
                await ctx.send(embed=Ledger.makeEmbed(ctx))

                # Use markdown to strikethrough payments made.
            else:
                await ctx.send(errorMsg)
        except ValueError:
            await ctx.send(errorMsg)
        except InvalidOperation:
            await ctx.send(errorMsg)

def setup(bot):
    bot.add_cog(UserCommands(bot))