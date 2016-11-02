from secret import BOT_TOKEN
from discord.ext import commands
from aiohttp import ClientSession
from util.checks import is_owner
from datetime import datetime
from math import ceil
from db.models import objects, Configuration
from secret import MIXPANEL_TOKEN
import base64
import json
import inspect
import os
import hashlib
import sys
import discord

bot = commands.Bot(command_prefix='`')
bot.start_time = datetime.now()
bot.remove_command('help')
bot.whttp = ClientSession()
bot.usage = {'total': 0}

cog_hashes = {}


@bot.event
async def on_ready():
    startup_extensions = [fn.replace('.py', '') for fn in os.listdir('./commands') if fn.endswith('.py')]

    for ext in startup_extensions:
        try:
            load_extension('commands.%s' % ext)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(ext, exc))
    print('\nLogged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    # Checking if recovering from error
    if sys.argv[1] == '98':
        await bot.send_message(discord.Object(id='241984924616359936'), 'Restarted.')
    elif sys.argv[1] != '-1':
        await bot.send_message(discord.Object(id='241984924616359936'), 'Recovered from a crash.')

    # Loading configurations into memory
    bot.configurations = {}
    configs = await objects.execute(Configuration.select())
    for c in configs:
        bot.configurations[c.server_id] = {}
        bot.configurations[c.server_id]['prefix'] = c.prefix


@bot.event
async def on_message(m):

    # Waiting till ready
    if not bot.__dict__.get('configurations'):
        return

    if m.channel.is_private:
        bot.command_prefix = '`'
    else:
        bot.command_prefix = bot.configurations[m.channel.server.id]['prefix'] or '`'

    # Checking if messages can be sent to the channel
    if m.channel.is_private or m.channel.permissions_for(m.channel.server.me).send_messages:
        await bot.process_commands(m)


@bot.event
async def on_command(command, ctx):

    # Not tracking if in testing
    if ctx.message.author.id == '136856172203474944':
        return

    bot.usage['total'] += 1
    bot.usage[command.name] = bot.usage.get(command.name, 0) + 1


@bot.event
async def on_command_completion(cmd, ctx):

    # Not tracking if in testing
    if ctx.message.author.id == '136856172203474944':
        return

    data = {
        'event': 'Command Used',
        'properties': {
            'token': MIXPANEL_TOKEN,
            'distinct_id': ctx.message.author.id,
            'command': cmd.name,
            'channel': ctx.message.channel.id,
            'server': ctx.message.channel.server.id if not ctx.message.channel.is_private else None,
            'username': ctx.message.author.name,
            'channel_name': ctx.message.channel.name,
            'server_name': ctx.message.channel.server.name if not ctx.message.channel.is_private else None,
            'arguments': ctx.kwargs
        }
    }
    data = base64.b64encode(bytes(json.dumps(data), 'UTF-8')).decode('UTF-8')

    async with bot.whttp.get('http://api.mixpanel.com/track?data=%s' % data) as r:
        pass


@bot.event
async def on_command_error(ex, ctx):

    # Did not pass any arguments
    if type(ex).__name__ == 'MissingRequiredArgument':
        await bot.send_message(ctx.message.channel,
                               'Missing arguments. Type `%s --help` to see what arguments you can pass.' %
                               ctx.message.content)
        return

    # Command does not exist
    if type(ex).__name__ == 'CommandNotFound':
        return

    if type(ex).__name__ == 'CommandInvokeError':
        m = 'An error occurred when executing a command.```yml\n' \
            'Command: %s\n' \
            'Exception: %s\n\n' \
            'Trace:\n' \
            '%s```' % (ctx.message.content, type(ex.original).__name__, str(ex.original))

        await bot.send_message(discord.Object(id='241984924616359936'), m)


@bot.event
async def on_server_remove(server):
        h = {'authorization': len(bot.servers), 'user-agent': 'Python:RunePy:v1.1.27 (by /u/duke605)'}
        url = 'https://bots.discord.pw/api/bots/%s/stats' % bot.user.id

        # Updating bot website stats
        async with bot.whttp.post(url, headers=h) as r:
            pass

        # Removing configurations
        await objects.execute(Configuration.select().where(Configuration.server_id == server.id).delete())


@bot.event
async def on_server_join(server):
    allowed = ceil(1.25 * sum([not m.bot for m in server.members]))
    owner = server.owner

    # Checking if the server has more bots than it is allowed
    if sum([m.bot for m in server.members]) <= allowed:
        h = {'authorization': len(bot.servers), 'user-agent': 'Python:RunePy:v1.1.27 (by /u/duke605)'}
        url = 'https://bots.discord.pw/api/bots/%s/stats' % bot.user.id

        # Adding configurations
        await objects.create(Configuration, id=server.id)

        # Updating bot website stats
        async with bot.whttp.post(url, headers=h) as r:
            pass

        return

    # Finding the first writable channel
    channels = sorted(server._channels, key=lambda c: server._channels[c].position)
    pub_channels = [server._channels[c] for c in channels
                    if server._channels[c].permissions_for(server.me).send_messages
                    and server._channels[c].permissions_for(server.me).read_messages
                    and server._channels[c].type == discord.ChannelType.text]

    # Checking if any writable channels found
    pub_channel = pub_channels[0] if pub_channels else owner

    # Sending messages
    await bot.send_message(discord.Object(id=241984924616359936),
                           'Left server **{}** for exceeding bot limit.\n'
                           '**Bots**: {:,}\n'
                           '**Users**: {:,}\n'
                           '**Allowed**: {:,}'
                           .format(server.name,
                                   sum([m.bot for m in server.members]),
                                   sum([not m.bot for m in server.members]),
                                   allowed))
    await bot.send_message(pub_channel,
                           '%s, your server, **%s**, exceeds the bots to users ratio. This bot is run on a '
                           'Raspberry PI with only 1 GB of RAM and can not afford to be sitting in a bot '
                           'collection server and not be used. If your server is not a bot collection '
                           'server and you do plan on actually using this bot please DM Duke605#4705 to '
                           'have your server added to a whitelist.' % (server.name, owner.mention))

    await bot.leave_server(server)


@bot.command()
async def invite():
    await bot.say('https://discordapp.com/oauth2/authorize?client_id=%s&scope=bot&permissions=93184' % bot.user.id)


@bot.group(aliases=['ext', 'cog'], hidden=True)
@is_owner()
async def extension():
    pass


@extension.command(hidden=True)
@is_owner()
async def load(ext: str, use_prefix=True):
    ext = ('commands.' if use_prefix else '') + ext

    try:
        load_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n{}'.format(ext, exc))
        return

    await bot.say('Successfully loaded extension **%s**.' % ext)


@extension.command(hidden=True)
@is_owner()
async def unload(ext: str, use_prefix=True):
    ext = ('commands.' if use_prefix else '') + ext

    try:
        bot.unload_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to unload extension {}\n{}'.format(ext, exc))
        return

    await bot.say('Successfully unloaded extension **%s**.' % ext)


@extension.command(hidden=True)
@is_owner()
async def reload(ext: str, use_prefix=True):
    ext = ('commands.' if use_prefix else '') + ext

    try:
        bot.unload_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to unload extension {}\n{}'.format(ext, exc))
        return

    try:
        load_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n{}'.format(ext, exc))
        return

    await bot.say('Successfully reloaded extension **%s**.' % ext)


@extension.command(hidden=True)
@is_owner()
async def refresh():
    counter = 0

    # Looping through hashes and reloading the different ones
    for key in cog_hashes:
        hash = cog_hashes[key]
        file = './%s.py' % key.replace('.', '/')

        # Getting hash
        with open(file, 'rb') as f:
            file_hash = hashlib.sha1(f.read()).hexdigest()

        # Comparing
        if hash == file_hash:
            continue

        # Unloading
        try:
            bot.unload_extension(key)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            await bot.say('Failed to unload extension {}\n{}'.format(key, exc))
            continue

        # reloading
        try:
            load_extension(key)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            await bot.say('Failed to load extension {}\n{}'.format(key, exc))
            continue

        counter += 1

    await bot.say('Reloaded **%s** cogs' % counter)


@bot.command(name='eval', hidden=True, pass_context=True)
@is_owner()
async def _eval(ctx, *, code):
    """Evaluates code."""
    python = '```py\n' \
             '# Input\n' \
             '{}\n\n' \
             '# Output\n' \
             '{}' \
             '```'

    env = {
        'bot': bot,
        'ctx': ctx,
        'message': ctx.message,
        'server': ctx.message.server,
        'channel': ctx.message.channel,
        'author': ctx.message.author,
        'os': os
    }

    env.update(globals())

    await bot.send_typing(ctx.message.channel)

    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(code, type(e).__name__ + ': ' + str(e)))
        return

    await bot.say(python.format(code, result or 'N/A'))


def load_extension(ext: str):
    bot.load_extension(ext)

    with open('./%s.py' % ext.replace('.', '/'), 'rb') as f:
        cog_hashes[ext] = hashlib.sha1(f.read()).hexdigest()


bot.run(BOT_TOKEN)
