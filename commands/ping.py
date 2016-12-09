from discord.ext import commands


class Ping:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description='Measures the latency between the bot and Discord.')
    async def ping(self, ctx):
        m = await self.bot.say('Pong')
        delta = m.timestamp - ctx.message.timestamp
        ms = int(round(delta.total_seconds() * 1000))
        await self.bot.edit_message(m, 'Pong: `%s`ms' % ms)


def setup(bot):
    bot.add_cog(Ping(bot))
