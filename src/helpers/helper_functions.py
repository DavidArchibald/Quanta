#!/usr/bin/env python3

import asyncio

import discord
from discord.ext import commands

import operator
import re

from ..constants import emojis

from .get_user_converter import GetUserConverter
from .bot_states import BotStates

states = BotStates()


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
        """Waits for a while. Mostly for testing .kill

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Keyword Arguments:
            time {int} -- How long to wait in seconds. (default: {1})
        """

        message = await ctx.send("Waiting...")

        await message.add_reaction(emojis.loading)
        await asyncio.sleep(time)

        await message.edit(content="Finished Waiting.")
        await message.remove_reaction(emojis.loading, ctx.bot.user)
        await message.add_reaction(emojis.yes)

    @commands.command(usage="unusable")
    @commands.check(lambda _: False)
    async def unusable(self, ctx: commands.Context):
        """Used for testing the Sudo command... or commands.check glitches

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        await ctx.send("This is supposed to be unusable... How're you using this?")


async def confirm_action(
    ctx: commands.context,
    message="Are you sure?",
    base_message=None,
    timeout: float = 60.0,
):
    """Checks if you're sure you want to continue.

    Arguments:
        ctx {commands.context} -- Information about where the command was run.

    Keyword Arguments:
        message {str} -- What it asks you about. (default: {"Are you sure?"})
        base_message {commands.Message} -- The message to use. (default: {None})
        timeout {float} -- How long to wait until canceling. (default: {60.0})

    Returns:
        (bool, commands.Message) -- The confirmation boolean and the message used to ask.
    """

    if base_message is not None:
        confirm = base_message.edit(content=message)
        try:
            await confirm.clear_reactions()
        except discord.HTTPException:
            pass
    else:
        confirm = await ctx.send(message)

    await confirm.add_reaction(emojis.yes)
    await confirm.add_reaction(emojis.no)

    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, _: reaction.message.id == confirm.id,
            )
        except asyncio.TimeoutError:
            await confirm.edit(content="Timeout out!")
            break

        if user == ctx.bot.user:
            continue

        if user == ctx.message.author and reaction.emoji in (emojis.yes, emojis.no):
            break

        try:
            await confirm.remove_reaction(reaction, user)
        except discord.HTTPException:
            pass

    try:
        await confirm.clear_reactions()
    except discord.HTTPException:
        await confirm.remove_reaction(emojis.yes, ctx.bot.user)
        await confirm.remove_reaction(emojis.no, ctx.bot.user)

    if reaction.emoji == emojis.yes:
        return (True, confirm)

    return (False, confirm)


def setup(bot, database):
    bot.add_cog(HelperCommands())
