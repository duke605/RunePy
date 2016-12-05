from discord.ext import commands
from collections import Counter
from datetime import datetime
import discord
import psutil


class About:

    def __init__(self, bot):
        self.bot = bot
        self.owner = None

    async def on_ready(self):
        self.owner = (await self.bot.application_info()).owner

    @property
    def version(self):
        return '1.2.0'

    def get_uptime(self):
        delta = datetime.utcnow() - self.bot.start_time
        seconds = delta.total_seconds()

        # Adding days if at least 1 day
        if seconds >= 86400:
            days = int(seconds / 86400)
            hours = int(seconds % 86400 / 3600)
            mins = int(seconds % 86400 % 3600 / 60)
            secs = int(round(seconds % 86400 % 3600 % 60))
            return '{:,}d {:,}h {:,}m {:,}s'.format(days, hours, mins, secs)

        # Default format
        hours = int(seconds / 3600)
        mins = int(seconds % 3600 / 60)
        secs = int(round(seconds % 3600 % 60))
        return '{:,}h {:,}m {:,}s'.format(hours, mins, secs)

    @commands.command(aliases=['info'], description='Shows information about this bot.')
    async def about(self):
        owner = self.owner
        e = discord.Embed()
        e.colour = 0x3572a7

        # Getting information
        unique_users = set(self.bot.get_all_members())
        unique_online = sum(1 for m in unique_users if str(m.status) != 'offline')
        channel_types = Counter(c.type for c in self.bot.get_all_channels())
        voice_channels = channel_types[discord.ChannelType.voice]
        text_channels = channel_types[discord.ChannelType.text]
        memory_usage = psutil.Process().memory_full_info().uss / 2**20
        total_commands = sum(self.bot.usage.values())
        top3_commands = self.bot.usage.most_common(3)
        total_users = sum(len(s.members) for s in self.bot.servers)
        total_online = sum(1 for m in self.bot.get_all_members() if str(m.status) != 'offline')

        command_column = '{:,} Total\n'
        member_column = '{:,} Total\n{:,} Total online\n{:,} Unique\n{:,} Unique online'
        channel_column = '{:,} Total\n{:,} Voice\n{:,} Text'

        if top3_commands:
            command_column += '\n'.join(['{} ({:,})'.format(c[0], c[1]) for c in top3_commands])

        e.add_field(name='Members', value=member_column.format(total_users, total_online, len(unique_users), unique_online))
        e.add_field(name='Channels', value=channel_column.format(text_channels + voice_channels, voice_channels, text_channels))
        e.add_field(name='Uptime', value=self.get_uptime())
        e.add_field(name='Servers', value='{:,}'.format(len(self.bot.servers)))
        e.add_field(name='Memory Usage', value='%.2f MiB' % memory_usage)
        e.add_field(name='Version', value=self.version)
        e.add_field(name='Commands', value=command_column.format(total_commands))
        e.set_author(name=str(owner), icon_url=owner.avatar_url)
        e.set_footer(text='Made with discord.py (%s)' % discord.__version__, icon_url='http://i.imgur.com/5BFecvA.png')

        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(About(bot))
