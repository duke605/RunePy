from secret import BOT_TOKEN
from discord.ext import commands
from aiohttp import ClientSession
from util.checks import is_owner
from datetime import datetime
from math import ceil
from db.models import objects, Configuration
from secret import MIXPANEL_TOKEN, DISCORD_BOTS_TOKEN
from collections import Counter
import base64
import json
import inspect
import os
import hashlib
import sys
import discord


def _get_prefix(bot, m):
    """Gets the prefix for a given server"""

    prefixes = ['`']
    channel = m.channel

    # Return normal prefix for private channel
    if not channel.is_private and bot.__dict__.setdefault('configurations', {}).get(channel.server.id, {}).get('prefix'):
        prefixes.append(bot.configurations[m.channel.server.id]['prefix'])

    return prefixes

bot = commands.Bot(command_prefix=_get_prefix)

# Adding custom attributes to bot
bot.start_time = datetime.utcnow()
bot.remove_command('help')
bot.whttp = ClientSession()
bot.usage = Counter()

cog_hashes = {}


@bot.event
async def on_ready():
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

    # Checking if messages can be sent to the channel
    if m.channel.is_private or m.channel.permissions_for(m.channel.server.me).send_messages:
        await bot.process_commands(m)


@bot.event
async def on_command(command, ctx):

    # Not tracking if in testing
    if ctx.message.author.id == '136856172203474944':
        return

    bot.usage[command.name] += 1


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
    async with bot.whttp.get('http://api.mixpanel.com/track?data=%s' % data):
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


@bot.command(description='Shows the oAuth link to invite this bot to a server.')
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


# Loading extensions
startup_extensions = ['commands.%s' % fn.replace('.py', '') for fn in os.listdir('./commands') if fn.endswith('.py')]
startup_extensions += ['tasks.%s' % fn.replace('.py', '') for fn in os.listdir('./tasks') if fn.endswith('.py')]

for ext in startup_extensions:
    try:
        load_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(ext, exc))
bot.run(BOT_TOKEN)
