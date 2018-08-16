#!/usr/bin/env python3

import asyncio

import discord
from discord.ext import commands

import operator
import re
import importlib

from ..constants import emojis
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
    else:
        confirm = await ctx.send(message)

    reaction = await wait_for_reactions(ctx, confirm, (emojis.yes, emojis.no))

    if reaction.emoji == emojis.yes:
        return (True, confirm)

    return (False, confirm)


async def wait_for_reactions(
    ctx: commands.Context,
    message: discord.message,
    reactions: iter,
    timeout: int = 60.0,
    remove_reactions=True,
):
    for reaction in list(reactions):
        try:
            await message.add_reaction(reaction)
        except (discord.NotFound, discord.InvalidArgument):
            reactions.remove(reaction)
        except discord.HTTPException:
            pass

    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, _: reaction.message.id == message.id,
            )
        except asyncio.TimeoutError:
            await message.edit(embed=None, content="Timeout out!")
            if remove_reactions == True:
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    for emoji in reactions:
                        await message.remove_reaction(emoji, ctx.bot.user)
            return None

        if user == ctx.bot.user:
            continue

        if user == ctx.message.author and reaction.emoji in reactions:
            break

        if remove_reactions == True:
            try:
                await message.remove_reaction(reaction, user)
            except (discord.HTTPException, discord.InvalidArgument):
                pass

    if remove_reactions == True:
        try:
            await message.clear_reactions()
        except discord.HTTPException:
            for reaction in reactions:
                await message.remove_reaction(ctx.bot.user, reaction)

    return reaction


def setup(bot, database):
    bot.add_cog(HelperCommands())
