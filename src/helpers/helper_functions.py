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

    @commands.command(usage="wait [time]")
    async def wait(self, ctx: commands.Context, time: int = 1):
        print("waiting")
        await asyncio.sleep(time)
        print("done waiting")


async def confirm_action(
    ctx: commands.context, message="Are you sure?", base_message=None
):
    yes = ctx.bot.get_emoji(475029940639891467)  # "<:quantacheck:475029940639891467>"
    no = ctx.bot.get_emoji(475032169086058496)  # "<:quantax:475032169086058496>"

    if base_message is not None:
        confirm = base_message.edit(message)
        confirm.clear_reactions()
    else:
        confirm = await ctx.send(message)

    await confirm.add_reaction(yes)
    await confirm.add_reaction(no)

    while True:
        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", timeout=15.0)
        except asyncio.TimeoutError:
            break

        if user == ctx.bot.user:
            continue

        if user == ctx.message.author and reaction.emoji in (yes, no):
            break

        try:
            await confirm.remove_reaction(reaction, user)
        except discord.HTTPException:
            pass

    await confirm.clear_reactions()

    if reaction.emoji == yes:
        return (True, confirm)

    return (False, confirm)


def setup(bot, database):
    bot.add_cog(HelperCommands())
