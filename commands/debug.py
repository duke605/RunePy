from discord.ext import commands
from datetime import datetime
import psutil


class Debug:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows information about the bot.')
    async def debug(self):
        _uptime = (datetime.now() - self.bot.start_time).total_seconds()

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
        m += '\nGuilds: {:,}'.format(len(self.bot.servers))
        m += '\nChannels: {:,}'.format(len([*self.bot.get_all_channels()]))
        m += '\nUsers: {:,}'.format(len([*self.bot.get_all_members()]))

        # Memory usage
        info = psutil.Process().memory_full_info()
        mem = info.uss / float(2**20)
        per = info.uss / psutil.virtual_memory().available
        m += '\nMemory_Usage: {:,} MiB ({}%)'.format(round(mem, 1), round(per, 1))

        # Command usages
        m += '\nCommands_This_Session: {:,} (avg. {:,}/min)'.format(self.bot.usage['total']
                                                                    , round(self.bot.usage['total']/(_uptime / 60), 2))

        # Finding most used command
        fav = None
        for key in self.bot.usage:
            usage = self.bot.usage[key]

            if key.lower() != 'total' and (fav is None or usage > fav[1]):
                fav = (key, usage)

        if fav:
            m += '\nMost_Used_Command: {} ({:,})'.format(*fav)

        await self.bot.say('```yml\n%s```' % m)


def setup(bot):
    bot.add_cog(Debug(bot))
