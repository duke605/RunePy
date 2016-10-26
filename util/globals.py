import aiohttp
from discord.ext import commands

http = aiohttp.ClientSession()
bot = commands.Bot(command_prefix='`')

