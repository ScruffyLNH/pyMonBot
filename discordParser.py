from operator import attrgetter, itemgetter
import nextcord # noqa
import Levenshtein as Lev
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
def fuzzyMatcher(unordered, sortBy):
    # Use fuzzy string matching to find nearest match 
    ratios = [Lev.ratio(u.display_name, sortBy) for u in unordered]
    # Generate a list of tuples (disp_name, id) by sorting according to ratios.
    ordered = [
        (x.display_name, str(x.id)) for _, x in sorted(
        zip(ratios,unordered),
        reverse=True,
        key=itemgetter(0)
    )
    ]
    # Convert list of tuples to dictionary and return.
    return dict(ordered)


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

def getUsersInVc(bot, ctx):
    if isinstance(ctx, nextcord.Interaction):
        author = ctx.user
    else:
        author = ctx.author
    voiceChannels = getVoiceChannelsByCategoryName(
        ctx,
        bot.config.contributerVoiceCategoryName,
    )

    voiceUsers = []
    if voiceChannels:
        for vc in voiceChannels:
            voiceUsers += vc.members

    # Exclude any bots and the invoker of the command.
    voiceUsers = list(
        filter(lambda s: not(s.bot or s.id == author.id), voiceUsers)
    )

    return voiceUsers

def arrangeShareUsers(author, shareUsers):
    """Reorders shareUsers and exludes shareUsers from any lower share
    multipliers than their max. Also makes an authorShare for the one invoking
    the command.

    Args:
        author (nextcord.Member): Nexcord member instance.
        shareUsers (Dict): A dictionary arranged by sharemultiplier as keys and
        list of nextcord.members as values.
    
    Returns:
        Dict, Dict shareUsers, authorShare
    """
    
    shareMultipliers = sorted(shareUsers, reverse=True)
    aggregate = set()
    authorShare = None
    for multiplier in shareMultipliers:
        suSet = set(shareUsers[multiplier])
        # Reorder and exclude shareusers that have already been put into a
        # multiplier key
        shareUsers[multiplier] = list(suSet - aggregate)
        aggregate |= suSet
        if author in shareUsers[multiplier]:
            authorShare = {multiplier: author}
    if not authorShare:
        authorShare = {Decimal(1.0): author}

    return shareUsers, authorShare


def filterVoiceConnected(shareUsers, usersInVoice):
    """Filter shareUsers based on the users present in applicable voice
    channels.

    Args:
        shareUsers (Dict): users arranged by shareMultiplier as key.
        usersInVoice (List): Users connected to applicable voice channel.

    Returns:
        Dict: Filtered shareUsers
    """
    shareMultipliers = sorted(shareUsers, reverse=True)
    aggregate = set()
    for multiplier in shareMultipliers:
        suSet = set(shareUsers[multiplier])
        shareUsersInVoice = set(usersInVoice).intersection(suSet)
        shareUsers[multiplier] = list(shareUsersInVoice)
        aggregate |= shareUsersInVoice
    leftOvers = list(set(usersInVoice) - aggregate) # Voice users without role.

    # Check if value 1.0 exists as key
    v = Decimal(1.0)
    if v in shareUsers:
        shareUsers[v] += leftOvers
    else:
        if leftOvers:
            shareUsers[v] = leftOvers

    return shareUsers