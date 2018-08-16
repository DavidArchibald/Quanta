#!/usr/bin/env python3

import discord
from discord.ext import commands

loading = None
cancel = None
yes = None
no = None

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

zzz = "\U0001F4A4"


def get_emojis(bot: commands.bot):
    global loading
    global cancel
    global yes
    global no

    loading = bot.get_emoji(478317750817914910)  # <quantaloading:478317750817914910>
    cancel = bot.get_emoji(475032169086058496)  # <:quantax:475032169086058496>
    yes = bot.get_emoji(475029940639891467)  # "<:quantacheck:475029940639891467>"
    no = bot.get_emoji(475032169086058496)  # "<:quantax:475032169086058496>"
