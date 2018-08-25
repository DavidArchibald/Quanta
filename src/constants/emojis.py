#!/usr/bin/env python3

import discord
from discord.ext import commands

loading = None
cancel = None
yes = None
no = None
cog = None
gear = None
circle_check = None
circle_x = None
radio_on = None
radio_off = None

sweat_smile = "U\1F605"

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
number_reactions = []

zzz_emoji = "\U0001f605"
zzz = None


def get_emojis(bot: commands.Bot):
    global loading
    global cancel
    global yes
    global no
    global cog
    global gear
    global circle_check
    global circle_x
    global radio_on
    global radio_off

    loading = bot.get_emoji(478317750817914910)  # <quantaloading:478317750817914910>
    cancel = bot.get_emoji(475032169086058496)  # <:quantax:475032169086058496>
    yes = bot.get_emoji(475029940639891467)  # "<:quantacheck:475029940639891467>"
    no = bot.get_emoji(475032169086058496)  # "<:quantax:475032169086058496>"
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

    global number_emojis
    global number_reactions

    for emoji in number_emojis:
        number_reactions.append(bot.get_emoji(emoji))

    global zzz
    zzz = bot.get_emoji(zzz_emoji)
