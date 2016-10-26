from secret import BOT_TOKEN
from discord.ext import commands
from aiohttp import ClientSession
from util.checks import is_owner
import inspect
import os

bot = commands.Bot(command_prefix='`')


@bot.event
async def on_ready():
    startup_extensions = [fn.replace('.py', '') for fn in os.listdir('./commands') if fn.endswith('.py')]

    for extension in startup_extensions:
        try:
            bot.load_extension('commands.%s' % extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    print('\nLogged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.whttp = ClientSession()


@bot.command()
async def invite():
    await bot.say('https://discordapp.com/oauth2/authorize?client_id=%s&scope=bot&permissions=93184' % bot.user.id)


@bot.group(aliases=['ext', 'cog'])
async def extension():
    pass


@extension.command()
@is_owner()
async def load(ext: str, use_prefix=True):
    ext = ('commands.' if use_prefix else '') + ext

    try:
        bot.load_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n{}'.format(ext, exc))
        return

    await bot.say('Successfully loaded extension **%s**.' % ext)


@extension.command()
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


@extension.command()
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
        bot.load_extension(ext)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n{}'.format(ext, exc))
        return

    await bot.say('Successfully reloaded extension **%s**.' % ext)


@bot.command(name='eval', hidden=True, pass_context=True)
@is_owner()
async def _eval(ctx, *, code):
    """Evaluates code."""
    python = '```py\n{}\n```'

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
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return

    await bot.say(python.format(result))


bot.run(BOT_TOKEN)
