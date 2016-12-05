from discord.ext import commands


def is_owner():
    """
    Checks if the caller of a command is ME
    """

    return commands.check(_is_owner())


def _is_owner():
    return lambda ctx: ctx.message.author.id == '136856172203474944'


def is_server_owner():
    """
    Checks if the caller is the server owner
    """

    return commands.check(_is_server_owner())


def _is_server_owner():
    return lambda ctx: not ctx.message.channel.is_private \
                       and ctx.message.channel.server.owner.id == ctx.message.author.id
