from discord.ext import commands
from datetime import datetime
import psutil


class Debug:

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @commands.command(description='Shows information about the bot.')
    async def debug(self):
        _uptime = (datetime.now() - self.start_time).total_seconds()

        days = int(_uptime / 86400)
        hours = int(_uptime % 86400 / 3600)
        minutes = int(_uptime % 86400 % 3600 / 60)
        seconds = int(round(_uptime % 86400 % 3600 % 60))

        # Uptime
        m = 'Uptime:'

        if days:
            m += ' {:,} day{}'.format(days, 's' if days != 1 else '')

        if hours:
            m += ' {:,} hour{}'.format(hours, 's' if hours != 1 else '')

        if minutes:
            m += ' {:,} minute{}'.format(minutes, 's' if minutes != 1 else '')

        if seconds:
            m += ' {:,} second{}'.format(seconds, 's' if seconds != 1 else '')

        # Connection numbers
        m += '\nConnected to {:,} guilds with {:,} channels and {:,} users.'.format(len(self.bot.servers),
                                                                                    len([*self.bot.get_all_channels()]),
                                                                                    len([*self.bot.get_all_members()]))

        # Memory usage
        info = psutil.Process().memory_full_info()
        mem = info.uss / float(2**20)
        per = info.uss / psutil.virtual_memory().available
        m += '\nMemory Usage: {:,} MiB ({}%)'.format(round(mem, 1), round(per, 1))

        await self.bot.say('```py\n%s```' % m)


def setup(bot):
    bot.add_cog(Debug(bot))
