#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import asyncio

import discord
from discord.ext import commands

import operator
import re

from .get_user_converter import GetUserConverter


class HelperCommands:
    # Helper Commands is currently exposed for testing purposes.
    pass


async def confirm_action(ctx: commands.context, message="Are you sure?"):
    confirm = await ctx.send(message)
    await confirm.add_reaction("✅")
    await confirm.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

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

    if str(reaction.emoji) == "✅":
        return True

    return False


def smallest(a: str, b: str):
    ab, ba = a + b, b + a
    if ab == ba:
        return 0
    if ab < ba:
        return -1
    return 1
