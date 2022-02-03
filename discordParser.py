from decimal import Decimal, InvalidOperation
    
async def getVoiceUsers():
    pass

def getSuperUserMentions(bot, ctx):
    mentions = ''
    for u in ctx.guild.members:
        if u.id in bot.config.superUsers:
            mentions += u.mention
    return mentions

def parseUsersWithShares(ctx):
    """Parses roles of the format <value><x> in to a dictionary.
    value is used for the key and the role's members as the dictionary value

    Args:
        ctx Class: discord.ext.commands.Context: Context from a discord command.

    Returns:
        Dict: Dictionary with share value as key and role id and value.
    """

    roles = ctx.guild.roles

    users = {}
    foundValues = []
    for role in roles:
        nameSplit = role.name.split('x')
        if len(nameSplit) == 2 and nameSplit[1] == '':
            try:
                value = Decimal(nameSplit[0])
                if value not in foundValues:
                    users[value] = role.members
                    foundValues.append(value)
            except InvalidOperation:
                pass
    return users

    # Return a dictionary with value and id 
    # i.e role= 1.2x return [{1.2(decimal):ID(int)}]

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
