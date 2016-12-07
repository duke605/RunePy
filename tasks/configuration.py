from math import ceil
from secret import DISCORD_BOTS_TOKEN
from db.models import objects, Configuration
import discord
import json


class Config:

    def __init__(self, bot):
        self.bot = bot

    async def _send_bot_limit_exceeded_message(self, server, allowed):
        """
        Sends a message to the onwer of the server the bot is leaving and the bot log informing why the bot has left

        :param server: The server the bot is leaving
        :param allowed: The number of allowed bots
        """

        owner = server.owner
        bots = sum([m.bot for m in server.members])
        users = sum([not m.bot for m in server.members])
        message = '%s, your server, **%s**, exceeds the bots to users ratio. This bot is run on a ' \
                  'Raspberry PI with only 1 GB of RAM and can not afford to be sitting in a bot '\
                  'collection server and not be used. If your server is not a bot collection '\
                  'server and you do plan on actually using this bot please DM Duke605#4705 to '\
                  'have your server added to a whitelist.' % (owner.mention, server.name)

        e = discord.Embed()
        e.title = server.name
        e.description = 'Exceeded bot limit.'
        e.add_field(name='Bots', value='{:,}'.format(bots))
        e.add_field(name='Users', value='{:,}'.format(users))
        e.add_field(name='Allowed', value='{:,}'.format(allowed))
        e.set_author(name=str(owner), icon_url=owner.avatar_url or owner.default_avatar_url)
        e.set_thumbnail(url=server.icon_url or owner.avatar_url or owner.default_avatar_url)

        await self.bot.send_message(owner, message)
        await self.bot.send_message(discord.Object(id=241984924616359936), embed=e)

    async def on_server_join(self, server):
        allowed = ceil(1.25 * sum([not m.bot for m in server.members]))

        # Checking if the server has more bots than it is allowed
        if sum([m.bot for m in server.members]) > allowed:
            await self._send_bot_limit_exceeded_message(server, allowed)
            return

        # Adding configurations
        await objects.create(Configuration, server_id=server.id)
        self.bot.configurations[server.id] = {'prefix': None}

        url = 'https://bots.discord.pw/api/bots/%s/stats' % self.bot.user.id
        data = {
            'headers': {
                'Authorization': DISCORD_BOTS_TOKEN,
                'User-Agent': 'Python:RunePy:v%s (by /u/duke605)' % self.bot.cogs['About'].version,
                'Content-Type': 'application/json'
            },
            'data': json.dumps({
                'server_count': len(self.bot.servers)
            })
        }

        # Updating bot website stats
        async with self.bot.whttp.post(url, **data):
            pass

        await self.bot.leave_server(server)

    async def on_server_remove(self, server):
        data = {
            'headers': {
                'authorization': DISCORD_BOTS_TOKEN,
                'user-agent': 'Python:RunePy:v%s (by /u/duke605)' % self.bot.cogs['About'].version,
                'Content-Type': 'application/json'
            },
            'data': json.dumps({
                'server_count': len(self.bot.servers)
            })
        }
        url = 'https://bots.discord.pw/api/bots/%s/stats' % self.bot.user.id

        # Updating bot website stats
        async with self.bot.whttp.post(url, **data):
            pass

        # Removing configurations
        await objects.execute(Configuration.raw('DELETE FROM configurations WHERE server_id = %s', server.id))
        del self.bot.configurations[server.id]


def setup(bot):
    bot.add_cog(Config(bot))
