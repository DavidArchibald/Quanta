#!/usr/bin/env python3

import discord
from discord.ext import commands

loading = None
cancel = None
yes = None
no = None


def get_emojis(bot: commands.bot):
    global loading
    global cancel
    global yes
    global no

    loading = bot.get_emoji(478317750817914910)  # <quantaloading:478317750817914910>
    cancel = bot.get_emoji(475032169086058496)  # <:quantax:475032169086058496>
    yes = bot.get_emoji(475029940639891467)  # "<:quantacheck:475029940639891467>"
    no = bot.get_emoji(475032169086058496)  # "<:quantax:475032169086058496>"
