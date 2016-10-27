from discord.ext import commands
from math import floor
from datetime import datetime
from util.arguments import Arguments
from shlex import split


class Vorago:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['rago'],
                      description='Shows the current rotation of Vorago and what the next one will be.')
    async def vorago(self, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='vorago')
        parser.add_argument('-H', '--hard-mode', action='store_true', help='Shows hardmode rotations.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        await self.execute(args)

    async def execute(self, args):
        rotations = (
            {
                'type': 'Ceiling Collapse',
                'unlock': 'Torso of Omens',
                'p10': ('Team Split', 'Green Bomb'),
                'p11': ('Team Split', 'Vitalis')
            },
            {
                'type': 'Scopulus',
                'unlock': 'Helm of Omens',
                'p10': ('Purple Bomb', 'Team Split'),
                'p11': ('Purple Bomb', 'Vitalis')
            },
            {
                'type': 'Vitalis',
                'unlock': 'Legs of Omens',
                'p10': ('Vitalis', 'Purple Bomb'),
                'p11': ('Vitalis', 'bleeds')
            },
            {
                'type': 'Green Bomb',
                'unlock': 'Boots of Omens',
                'p10': ('Green Bomb', 'Vitalis'),
                'p11': ('Green Bomb', 'Team Split')
            },
            {
                'type': 'Team Split',
                'unlock': 'Maul of Omens',
                'p10': ('Team Split', 'Team Split'),
                'p11': ('Team Split', 'Purple Bomb')
            },
            {
                'type': 'The End',
                'unlock': 'Gloves of Omens',
                'p10': ('Purple Bomb', 'Bleeds'),
                'p11': ('Purple Bomb', 'Vitalis')
            }
        )

        ms = round(datetime.utcnow().timestamp() * 1000)
        current = floor((((floor(floor(ms / 1000) / (24 * 60 * 60))) - 6) % (7 * len(rotations))) / 7)
        days_until = 7 - ((floor((ms / 1000) / (24 * 60 * 60))) - 6) % (7 * len(rotations)) % 7
        next = current + 1 if current + 1 < len(rotations) else 0

        m = '**Curent Rotation**: %s.\n' % rotations[current]['type']
        m += '**Next Rotation**: %s in `%s` day%s.' % (rotations[next]['type'], days_until,
                                                       's' if days_until == 1 else '')

        # Adding hard mode information
        if args.hard_mode:
            m += '\n\n**__Hard mode__**:\n'
            m += '**Phase 10**: %s + %s.\n' % rotations[current]['p10']
            m += '**Phase 11**: %s + %s.\n' % rotations[current]['p11']
            m += '**Unlock**: %s' % rotations[current]['unlock']

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Vorago(bot))
