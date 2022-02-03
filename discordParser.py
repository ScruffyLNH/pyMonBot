import discord # noqa
    
async def getVoiceUsers():
    pass

def getVoiceChannelsByCategoryName(ctx, name):
    
    categories = ctx.guild.categories
    categoryChannel = None
    for c in categories:
        if c.name.upper() == name.upper():
            categoryChannel = c
            break
    
    if categoryChannel:
        return categoryChannel.voice_channels
    else:
        return None

async def getTrackedVoiceChannels():
    pass

def getShareholders(bot, ctx):
    
    voiceChannels = getVoiceChannelsByCategoryName(
        ctx,
        bot.config.contributerVoiceCategoryName,
    )

    shareHolders = []
    if voiceChannels:
        for vc in voiceChannels:
            shareHolders += vc.members

    # Exclude any bots and the invoker of the command.
    shareHolders = list(
        filter(lambda s: not(s.bot or s.id == ctx.author.id), shareHolders)
    )

    return shareHolders
