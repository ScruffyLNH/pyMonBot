import discord # noqa
import os
import logging
import configuration
import ledger
from logging import handlers
from discord.ext import commands
from constants import Constants
from utility import loadData, saveData
from pydantic import ValidationError
from discord.ext import commands


if __name__ == "__main__":
    """Instanciate the discord.py bot and deserialize data.
    """
    # Generate intents. Why? Because discord, that's why.
    intents = discord.Intents.default()
    intents.members = True
    # Instaciate bot and set the command prefix.
    bot = commands.Bot(Constants.CMD_PREFIX, intents = intents)

    # Setup the logger
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = handlers.RotatingFileHandler(
        filename=Constants.LOG_FILENAME,
        mode='a', # Append mode
        maxBytes=8*1024*1024, # Max size is 8MB
        backupCount=1,
        encoding='utf-8'
    )
    handler.setFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    )
    logger.addHandler(handler)
    bot.logger = logger

    # Deserialize configuration data.
    configData = loadData(Constants.CONFIG_DATA_FILENAME)
    if configData is None:
        bot.logger.info('Config data was not found.')
        bot.config = configuration.Configuration()
        configData = bot.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)
    else:
        try:
            # Attempt to parse persistent config data to config.
            bot.config = configuration.Configuration.parse_obj(
                configData
            )
            bot.logger.info(
                'Config data successfully parsed.'
            )
        except ValidationError as e:
            bot.logger.warning(
                'Excption thrown, config data found but could not be parsed.\n'
                f'{e}\n'
                'Starting clean.'
            )

            bot.config = configuration.Configuration()
            configData = bot.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)

    # Deserialize accounting data
    _ledger = loadData(Constants.LEDGER_FILENAME)
    if _ledger is None:
        bot.logger.info('No ledger found. Starting clean.')
        bot.ledger = ledger.Ledger()
        _ledger = bot.ledger.json(indent=2)
        saveData(Constants.LEDGER_FILENAME)
    else:
        try:
            # Attempt to parse ledger data.
            bot.ledger = ledger.Ledger.parse_obj(
                _ledger
            )
            bot.logger.info(
                'Ledger successfully parsed'
            )
            print(
                'Ledger successfully parsed.\n'
                f'Found {len(bot.ledger.contributions)} contributions.'
            )
        except ValidationError as e:
            bot.logger.warning(
                'Exception thrown, could not validate existing ledger.\n'
                f'{e}\n'
                'Record was found, but could not be loaded.\n'
                'Starting clean.'
            )
        # TODO: Dry wet code. Make a general function to generate bot data.
        bot.ledger = ledger.Ledger()
        _ledger = bot.ledger.json(indent=2)
        saveData(Constants.LEDGER_FILENAME)

# Check functions
def isAdmin(ctx):
    return ctx.author.id == bot.config.adminId

# Events
@bot.event
async def on_ready():
    bot.logger.info('on_ready event triggered.')
    print('Bot is ready!')

# Commands
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
@commands.check(isAdmin)
async def load(ctx, extension):
    """Load a specific cog.

    Args:
        extension (string): Name of the cog to be loaded
    """
    return None

@bot.command()
@commands.check(isAdmin)
async def unload(ctx, extension):
    """Unloads a specific cog

    Args:
        extension (string): The name of the cog to be unloaded.
    """
    return None

@bot.command()
@commands.check(isAdmin)
async def reload(ctx, extension):
    """Reloads a specific cog

    Args:
        extension (string): Name of the cog to be reloaded.
    """
    bot.reload_extension(f'cogs.{extension}')

# Load cogs
for filename in os.listdir('./cogs'):
    # Files in exclusion list will not be loaded.
    exclusionList = [
        '__init__.py',
    ]
    if filename not in exclusionList:
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

# Deserialize token
token = loadData('token.json')
# Run bot using token.
bot.run(token)