from discord.ext import commands
from util.arguments import Arguments
from util.image_util import text_to_image
from shlex import split
import re


class Imagify:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['image'],
                      description='Searches through the chat to find a table-like message if an id is not provided and '
                                  'turns the table into an image. (Useful for mobile users)')
    async def imagify(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='imagify')
        parser.add_argument('id', nargs='?', type=int,
                            help='The id of the table-like message. Leave blank to use latest.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Getting the id of the latest message that looks like a table
        if args.id is None:

            # Finding table
            async for message in self.bot.logs_from(ctx.message.channel, before=ctx.message.id):

                # Checking if table like
                if re.search(r"^```\.-.*-'```$", message.content, re.S):
                    args.id = message.id
                    break

        # Checking if message id found
        if args.id is None:
            await self.bot.say('A table-like message could not be found.')
            return

        await self.execute(ctx, args)

    async def execute(self, ctx, args):
        message = await self.bot.get_message(ctx.message.channel, args.id)

        # Checking if message was found
        if message is None or not re.search(r"^```\.-.*-'```$", message.content, re.S):
            await self.bot.say('A table-like message with the id **%s** could not be found.' % args.id)
            return

        text = re.search(r"^```(.*)```$", message.content, re.S).group(1)
        link = await text_to_image(text)

        # Checking if the image could be uploaded
        if not link:
            await self.bot.say('The table-like message could not be uploaded to imgur.')
            return

        await self.bot.say(link)


def setup(bot):
    bot.add_cog(Imagify(bot))
