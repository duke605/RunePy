from secret import BOT_TOKEN
from discord.ext import commands
from aiohttp import ClientSession
from util.checks import is_owner
import inspect
import os
import hashlib
import sys
import discord

bot = commands.Bot(command_prefix='`')
bot.triggers = {'110373943822540800': '&'}
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
    if sys.argv[1] == '99':
        await bot.send_message(discord.Object(id='241984924616359936'), 'Restarted.')
    elif sys.argv[1] != '98' and sys.argv[1] != '-1':
        await bot.send_message(discord.Object(id='241984924616359936'), 'Recovered from a crash.')


@bot.event
async def on_message(m):
    if m.channel.server:
        bot.command_prefix = bot.triggers.get(m.channel.server.id, '`')
    else:
        bot.command_prefix = '`'

    await bot.process_commands(m)


@bot.event
async def on_command(command, ctx):

    # Not tracking if in testing
    if ctx.message.author.id == '136856172203474944':
        return

    bot.usage['total'] += 1
    bot.usage[command.name] = bot.usage.get(command.name, 0) + 1


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


@bot.command()
async def invite():
    await bot.say('https://discordapp.com/oauth2/authorize?client_id=%s&scope=bot&permissions=93184' % bot.user.id)


@bot.group(aliases=['ext', 'cog'], hidden=True)
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

    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(code, type(e).__name__ + ': ' + str(e)))
        return

    await bot.say(python.format(code, result))


def load_extension(ext: str):
    bot.load_extension(ext)

    with open('./%s.py' % ext.replace('.', '/'), 'rb') as f:
        cog_hashes[ext] = hashlib.sha1(f.read()).hexdigest()

bot.run(BOT_TOKEN)
