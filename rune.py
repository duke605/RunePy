from secret import BOT_TOKEN
from discord import __version__
from discord.ext import commands
from aiohttp import ClientSession
from util.checks import is_owner

bot = commands.Bot(command_prefix='`')


@bot.event
async def on_ready():
    startup_extensions = ['araxxi', 'circus', 'clear', 'lamp', 'peng_locs', 'portables', 'price', 'stats', 'vos', 'xp']

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


@bot.command(aliases=['info'])
async def about():
    await bot.say('__Author:__ Duke605\n'
                  '__Library:__ discord.py (' + __version__ + ')\n'
                  '__Version:__ 1.1.0\n'
                  '__Github Repo:__ <https://github.com/duke605/RunePy>\n'
                  '__Official Server:__ <https://discord.gg/uaTeR6V>')


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


bot.run(BOT_TOKEN)
