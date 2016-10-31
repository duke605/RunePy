from discord.ext import commands
from util.image_util import text_to_image


class Help:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['commands'], description='Shows this command.')
    async def help(self, ctx):
        keys = [k for k in self.bot.commands if not self.bot.commands[k].hidden
                and k not in self.bot.commands[k].aliases]

        # Building message
        messages = []
        m = ''
        for key in keys:
            command = self.bot.commands[key]

            temp = '%s:\n' % key
            temp += "\taliases: '%s'\n" % ("', '".join(command.aliases) if command.aliases else 'None')
            temp += '\tdescription: %s\n\n' % (command.description if command.description else 'N/A')

            # Limit reached starting new message
            if len(temp) + len(m) >= 2000:
                messages.append(m)
                m = ''

            m += temp

        messages.append(m)
        for message in messages:
            await self.bot.send_message(ctx.message.author, '```yml\n%s```' % message)


def setup(bot):
    bot.add_cog(Help(bot))
