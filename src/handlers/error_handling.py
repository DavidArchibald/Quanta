#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio
import sys
import traceback

import itertools

import fuzzywuzzy
from fuzzywuzzy import process

from ..constants import emojis
from ..helpers import helper_functions
from ..helpers.helper_functions import wait_for_reactions


class CommandErrorHandler:
    """Handles any errors the bot will throw."""

    def __init__(self, database):
        self.database = database

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """The event triggered when an error is raised while invoking a command.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.s
            error {Exception} -- The error the bot comes across.
        """

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)
        command = ctx.message.content.split(" ")[0][len(ctx.prefix) :]

        if isinstance(error, commands.CommandNotFound):
            all_command_names = list(
                itertools.chain(
                    *[[*command.aliases, command.name] for command in ctx.bot.commands]
                )
            )
            closest_command_name, closest_ratio = process.extractOne(
                command, all_command_names
            )

            no_command = f"I don't have the command `{command}`, sorry!"
            try_help_command = (
                f"Try using `{ctx.prefix}help` for information about my commands."
            )
            if closest_ratio < 80:
                await ctx.send(f"{no_command} {try_help_command}")
            else:
                message = await ctx.send(
                    f"Did you mean to use `{ctx.prefix}{closest_command_name}`?"
                )
                reaction = await wait_for_reactions(
                    ctx, message, (emojis.yes, emojis.no), timeout=10
                )
                if reaction is None:
                    await message.edit(content=try_help_command)
                    return
                if reaction.emoji == emojis.yes:
                    await message.edit(
                        content=f"I'll run the command `{closest_command_name}`` for you :)"
                    )
                    await asyncio.sleep(1)
                    await message.delete()
                    new_message = ctx.message
                    _, arguments = new_message.content.split(" ", 1)
                    new_message.content = (
                        f"{ctx.prefix}{closest_command_name} {arguments}"
                    )

                    await ctx.bot.process_commands(new_message)
                    return

            return
        elif isinstance(error, discord.Forbidden):
            print(error)
            await ctx.send(
                f"I don't have the permissions to do that, sorry! I need the"
            )
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f'"{command}" has been disabled.')
            return
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(f'"{command}" cannot be used in Private Messages.')
                return
            except discord.Forbidden:
                pass

        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )


def setup(bot, database):
    bot.add_cog(CommandErrorHandler(database))
