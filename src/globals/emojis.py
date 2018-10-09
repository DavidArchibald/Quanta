#!/usr/bin/env python3

from discord.ext import commands

loading = None
cancel = None
yes = check = None
no = error = x = None
cog = None
gear = None
circle_check = None
circle_x = None
radio_on = None
radio_off = None
empty = None

sweat_smile = "\U0001F605"

number_emojis = [
    "0\u20e3",  # zero
    "1\u20e3",  # one
    "2\u20e3",  # two
    "3\u20e3",  # three
    "4\u20e3",  # four
    "5\u20e3",  # five
    "6\u20e3",  # six
    "7\u20e3",  # seven
    "8\u20e3",  # eight
    "9\u20e3",  # nine
    "\U0001f51f",  # ten
]

zzz = "\ud83d\udca4"


def get_emojis(bot: commands.Bot):
    global loading
    global cancel
    global yes
    global check
    global no
    global error
    global x
    global cog
    global gear
    global circle_check
    global circle_x
    global radio_on
    global radio_off
    global empty

    loading = bot.get_emoji(478317750817914910)  # <quantaloading:478317750817914910>
    cancel = bot.get_emoji(475032169086058496)  # <:quantax:475032169086058496>
    yes = check = bot.get_emoji(
        475029940639891467
    )  # "<:quantacheck:475029940639891467>"
    no = error = x = bot.get_emoji(
        475032169086058496
    )  # "<:quantax:475032169086058496>"
    cog = bot.get_emoji(479811570440863750)  # <quantagear:479811570440863750>
    gear = cog
    circle_check = bot.get_emoji(
        482275155834568739
    )  # <:quantacirclecheck:482275155834568739>
    circle_x = bot.get_emoji(482275203523805185)  # <:quantacirclex:482275203523805185>
    radio_on = bot.get_emoji(482275278807236633)  # <:quantaradioon:482275278807236633>
    radio_off = bot.get_emoji(
        482275329201930250
    )  # <:quantaradiooff:482275329201930250>
    empty = bot.get_emoji(488182956133974017)  # "<:quantaempty:488182956133974017>"
