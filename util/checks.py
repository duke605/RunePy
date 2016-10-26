from discord.ext import commands


def is_owner():
    """
    Checks if the caller of a command is ME
    """

    return commands.check(lambda ctx: ctx.message.author.id == '136856172203474944')
