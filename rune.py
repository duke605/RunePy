from util.globals import bot
from secret import BOT_TOKEN
from discord import __version__
from commands import araxxi_command, circus_command, clear_command, lamp_command, peng_command, portables_command, \
    price_command, reset_command, stats_command, vos_command, xp_command


@bot.event
async def on_ready():
    print('==============================')
    print('{:^31}'.format('Connected.'))
    print('==============================')


@bot.command(aliases=['info'])
async def about():
    await bot.say('__Author:__ Duke605\n'
                  '__Library:__ discord.py (' + __version__ + ')\n'
                  '__Version:__ 1.0.10\n'
                  '__Github Repo:__ <https://github.com/duke605/RunePy>\n'
                  '__Official Server:__ <https://discord.gg/uaTeR6V>')


@bot.command()
async def invite():
    await bot.say('https://discordapp.com/oauth2/authorize?client_id=%s&scope=bot&permissions=93184' % bot.user.id)

bot.run(BOT_TOKEN)
