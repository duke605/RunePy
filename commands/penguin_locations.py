from discord.ext import commands


class PenguinLocations:

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.command(aliases=['pengs', 'peng', 'penguin', 'penguins'], pass_context=True,
                      description='Shows the location of penguins in world 60.')
    async def penglocs(self, ctx):
        await self.bot.send_typing(ctx.message.channel)

        async with self.bot.whttp.get('http://2016.world60pengs.com/rest/index.php?m=activepenguin') as r:
            data = await r.json()

        async with self.bot.whttp.get('http://2016.world60pengs.com/rest/index.php?m=bear&a=active') as r:
            bear = await r.json()

        m = '__**World 60 Penguin Locations**__:\n\n'
        for i, loc in enumerate(data):
            m += '%s.) __**%s**__: %s (%s point%s)\n' \
                 '**Confined To**: %s\n' \
                 '**Last Seen**: %s\n\n' \
                 % (i+1, loc['name'], loc['disguise'], loc['points'], 's' if loc['points'] != 1 else ''
                                              , loc['confined_to'], loc['last_location'])

        m += '%s.) __**%s**__: Polar Bear (1 point)\n' \
             '%s' % (len(data) + 1, bear[0]['name'], bear[0]['location'])

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(PenguinLocations(bot))