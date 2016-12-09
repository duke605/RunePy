from secret import DISCORD_BOTS_TOKEN
from db.models import objects, Configuration
from datetime import datetime, timedelta
from secret import MIXPANEL_SECRET
import asyncio
import base64
import discord
import json
import util


class Config:

    def __init__(self, bot):
        self.bot = bot
        self.prune_servers_task = bot.loop.create_task(self.prune_servers())

    @util.ignore_exceptions(exception_handler=lambda info: None)
    def __unload(self):
        self.prune_servers_task.cancel()

    async def _send_parting_message(self, server):
        """
        Sends a message to the server owner and bot log telling the owner why the bot left the server

        :param server: The server the bot is leaving
        """

        owner = server.owner
        bots = sum(m.bot for m in server.members)
        users = sum(not m.bot for m in server.members)
        message = '{0}, your server, **{1}**, has not used {2} in 14 or more days. To keep the bot statistics accurate and reduce memory ' \
                  'usage {2} will leave your server. If you wish to use {2}, but don\'t plan on using it at least once every 14 days, ' \
                  'please join the official development server <http://bit.ly/Duke605Development>. If you do plan on using {2} more ' \
                  'than every 14 days, use the following link to invite {2} back to your server <http://bit.ly/Rune-Py>.'

        e = discord.Embed()
        e.title = server.name
        e.timestamp = server.me.joined_at
        e.description = 'Did not use the more for 14 or more days.'
        e.add_field(name='Bots', value='{:,}'.format(bots))
        e.add_field(name='Users', value='{:,}'.format(users))
        e.set_author(name=str(owner), icon_url=owner.avatar_url or owner.default_avatar_url)
        e.set_thumbnail(url=server.icon_url or owner.avatar_url or owner.default_avatar_url)

        await self.bot.send_message(owner, message.format(owner.mention, server.name, server.me.mention))
        await self.bot.send_message(discord.Object(id=241984924616359936), embed=e)

    @util.ignore_exceptions_async()
    async def _get_command_usages(self):
        """
        Uses the Mixpanel API to call a script and get the past 2 nights of command usages
        """

        # Getting script
        with open('assets/scripts/command_usages.js') as file:
            script = file.read()

        data = {
            'url': 'https://mixpanel.com/api/2.0/jql',
            'headers': {
                'authorization': 'Basic %s' % base64.b64encode(bytes(MIXPANEL_SECRET + ':', encoding='UTF-8')).decode('utf-8')
            },
            'params': {
                'script': script,
                'params': json.dumps({
                    'from_date': (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d'),
                    'to_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
                })
            }
        }

        # Getting usages
        async with self.bot.whttp.get(**data) as r:

            if r.status != 200:
                return None

            data = {usage['key'][0]: usage['value'] for usage in await r.json()}
            return data

    @util.ignore_exceptions_async()
    async def _evaluate_server(self, server, usages):
        """
        Evaluates a server to see if it should be left

        :param server: The server to evaluate
        :param usages: The command usages for the past 2 weeks
        """

        commands_used = usages.get(server.id, 0)
        if commands_used <= 0 and (server.me.joined_at + timedelta(days=14)) <= datetime.utcnow():
            await self._send_parting_message(server)
            await self.bot.leave_server(server)

    async def prune_servers(self):
        """
        Leaves servers that have not used the bot in 2 weeks or 1 fortnight or 14 days
        """
        await self.bot.wait_until_ready()

        while not self.bot.is_closed:

            # Getting command usages for the last 2 weeks
            usages = await self._get_command_usages()
            if not usages:
                continue

            # Evaluating servers
            servers = [s for s in self.bot.servers]
            for server in servers:

                # Skipping my server
                if server.id in ('240109767970783233', '110373943822540800'):
                    continue

                # Evaluating if server should be left
                await self._evaluate_server(server, usages)

            # Waiting 1 hour
            del usages, servers
            await asyncio.sleep(60 * 60)

    @util.ignore_exceptions_async()
    async def _update_server_count(self):
        """
        Updates bot's server count on bots.discord.pw
        """

        data = {
            'url': 'https://bots.discord.pw/api/bots/%s/stats' % self.bot.user.id,
            'headers': {
                'Authorization': DISCORD_BOTS_TOKEN,
                'User-Agent': 'Python:RunePy:v%s (by /u/duke605)' % self.bot.cogs['About'].version,
                'Content-Type': 'application/json'
            },
            'data': json.dumps({
                'server_count': len(self.bot.servers)
            })
        }

        async with self.bot.whttp.post(**data):
            pass

    async def on_server_join(self, server):
        await objects.create(Configuration, server_id=server.id)
        await self._update_server_count()
        self.bot.configurations[server.id] = {'prefix': None}

    async def on_server_remove(self, server):
        await self._update_server_count()
        await objects.execute(Configuration.raw('DELETE FROM configurations WHERE server_id = %s', server.id))
        del self.bot.configurations[server.id]


def setup(bot):
    bot.add_cog(Config(bot))
