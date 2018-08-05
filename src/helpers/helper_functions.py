#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import asyncio

import discord
from discord.ext import commands

import operator
import re
from .bot_states import BotStates

states = BotStates()

from .get_user_converter import GetUserConverter


class HelperCommands:
    # Helper Commands is currently exposed for testing purposes.
    @commands.command(usage="error [error]")
    async def error(self, ctx: commands.Context):
        try:
            1 / 0
        except ZeroDivisionError as exception:
            await states.error(ctx, exception)


async def confirm_action(ctx: commands.context, message="Are you sure?"):
    yes = ctx.bot.get_emoji(475029940639891467)  # "<:quantacheck:475029940639891467>"
    no = ctx.bot.get_emoji(475032169086058496)  # "<:quantax:475032169086058496>"

    confirm = await ctx.send(message)
    await confirm.add_reaction(yes)
    await confirm.add_reaction(no)

    def check(reaction, user):
        return user == ctx.message.author and reaction in [yes, no]

    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add", timeout=15.0, check=check
            )
        except asyncio.TimeoutError:
            await confirm.delete()
            return False

        try:
            await confirm.remove_reaction(reaction, user)
        except discord.HTTPException:
            pass

    await confirm.delete()

    if reaction == yes:
        return True

    return False


def smallest(a: str, b: str):
    ab, ba = a + b, b + a
    if ab == ba:
        return 0
    if ab < ba:
        return -1
    return 1
