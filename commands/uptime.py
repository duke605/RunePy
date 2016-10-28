from discord.ext import commands
from datetime import datetime


class Uptime:

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @commands.command(description='Shows how long this bot has been running.')
    async def uptime(self):
        _uptime = (datetime.now() - self.start_time).total_seconds()

        days = _uptime / 60 / 60 / 24
        hours = days % 1 * 60
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60

        # Cleaning
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(round(seconds))

        m = 'Active for'

        if days:
            m += ' **{:,}** day{}'.format(days, 's' if days != 1 else '')

        if hours:
            m += ' **{:,}** hour{}'.format(hours, 's' if hours != 1 else '')

        if minutes:
            m += ' **{:,}** minute{}'.format(minutes, 's' if minutes != 1 else '')

        if seconds:
            m += ' **{:,}** second{}'.format(seconds, 's' if seconds != 1 else '')

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Uptime(bot))
