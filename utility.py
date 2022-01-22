import json
import os
import logging


def loadData(fileName):
    """Load data from persitent file. Returns None of file is not found.

    :param fileName: Name of the file to load from.
    :type fileName: string
    :return: The data that was loaded
    :rtype: var, None
    """
    try:
        assert os.stat(fileName).st_size != 0
        with open(fileName) as f:
            data = json.load(f)
    except AssertionError:
        logger = logging.getLogger('discord')
        logger.info(
            'Exception thrown when trying to load data.\n'
            f'Assertion failed: {fileName} should not be empty.\n'
        )
        data = None
    except FileNotFoundError as e:
        logger = logging.getLogger('discord')
        logger.info(
            'Exception thrown when trying to load data. '
            'Error message reads:\n'
            f'{e}\n'
        )
        data = None
    return data


def saveData(fileName, data):
    """Save data to persistent file. If file does not already exist it will
    be created. The function will return True if successful, else False.

    :param fileName: Name of the file to save to.
    :type fileName: string
    :param data: The data object to save
    :type data: var
    :return: Status. True if successful, False if unsuccessful.
    :rtype: bool
    """
    try:
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        logger = logging.getLogger('discord')
        logger.warning(
            'Exception thrown when trying to serialize data. '
            'Error message reads as follows:\n'
            f'{e}\n'
        )
        return False
    return True


def formatData(obj):
    """format data into json string using the dictionary structure as default.
    :param obj: The python object to be formatted.
    :type obj: object
    :return: The object data parsed into json string, or None if formatting was
    unsuccessful.
    :rtype: string, None
    """
    try:
        jsonData = json.dumps(
            obj,
            default=lambda o: o.__dict__,
            indent=2
        )
    except Exception as e:
        logger = logging.getLogger('discord')
        logger.warning(
            'Exception thrown while attempting to format data. '
            'Error message reads as follows:\n'
            f'{e}\n'
        )
        return None
    return jsonData


def checkConfig(config):
    """Checks that all necessary configuration fields has been set.
    Returns the names of any invalid configuration fields.

    :param config: The Configuration object to check.
    :type confing: configuration.Configuration
    :return: Names of fields that have yet to be set.
    :return type: List[str]
    """

    remainingFields = [
        f for f in dir(config)
        if not f.startswith('_')
        and not f == 'fields'
        and not callable(getattr(config, f))
        and not type(getattr(config, f)) is int
    ]

    return remainingFields


def getConfigIds(config):
    """Get a list of all config fields that have been set along with the ID.

    :param config: The configuration object
    :type config: configuration.Configuration
    """
    fields = [
        f + ': ' + str(getattr(config, f)) for f in dir(config)
        if not f.startswith('_')
        and not f == 'fields'
        and not callable(getattr(config, f))
        and type(getattr(config, f)) is int
    ]

    return fields


def unformatData(fileName):
    pass


def initialize(clientObject):
    pass
    # Post resources to resource channel

    # Get the URL links to resourses

    # Identify the org logo url and store the link in Constants class


async def sendMessagePackets(ctx, message, limit=1800):
    lines = message.split('\n')
    msgPacket = []
    packets = []
    runningTotal = 0

    # Split message to smaller chunks for which the number of characters
    # will not exceed 1800.
    for i, line in enumerate(lines):
        runningTotal += len(line)
        if runningTotal <= 1800:
            msgPacket.append(line)
            if i == len(lines) - 1:
                packets.append(msgPacket)
        else:
            packets.append(msgPacket)
            runningTotal = len(line)
            msgPacket = [line]

        # Add to total charactes for each newline that will be added.
        runningTotal += 1

    for msgPacket in packets:
        await ctx.send('\n'.join(msgPacket))
