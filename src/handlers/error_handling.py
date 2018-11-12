#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio
import sys
import traceback

from fuzzywuzzy import process

from ..globals import emojis
from ..helpers.helper_functions import wait_for_reactions


class CommandErrorHandler:
    """Handles any errors the bot will throw."""

    async def on_command_error(self, ctx: commands.Context, error: BaseException):
        """The event triggered when an error is raised while invoking a command.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
            error {Exception} -- The error the bot comes across.
        """

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)
        if isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.NoPrivateMessage):
                await ctx.send(
                    f"The command `{ctx.invoked_with}` can't be used in a DM."
                )
                return
            elif isinstance(error, commands.BotMissingPermissions):
                if len(error.missing_perms) == 1:
                    missing_permissions = error.missing_perms[0]
                elif len(error.missing_perms) == 2:
                    missing_permissions = (
                        f"{error.missing_perms[0]} and {error.missing_perms[1]}"
                    )
                else:
                    missing_permissions = (
                        ", ".join(error.missing_perms[:-1])
                        + ", and"
                        + error.missing_perms[-1]
                    )

                    await ctx.send(
                        f"I don't have the permissions: {missing_permissions}) to"
                    )
                return
            is_owner = await ctx.bot.is_owner(ctx.message.author)
            if is_owner is True:
                await ctx.command.reinvoke(ctx)
            else:
                await ctx.send(
                    f"You can't use the command `{ctx.invoked_with}`, sorry!"
                )
        elif isinstance(error, commands.CommandNotFound):
            if ctx.prefix == "":
                return
            all_command_names = [
                name
                for command in ctx.bot.commands
                if command.hidden is not True
                for name in (*command.aliases, command.name)
            ]

            closest_command_name, closest_ratio = process.extractOne(
                ctx.invoked_with, all_command_names
            )

            no_command = f"I don't have the command `{ctx.invoked_with}`, sorry!"
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
                if reaction is None or reaction.emoji == emojis.no:
                    await message.edit(content=try_help_command)
                elif reaction.emoji == emojis.yes:
                    await message.edit(
                        content=(
                            f"I'll run the command `{closest_command_name}` for you."
                        )
                    )
                    await asyncio.sleep(1)
                    new_message = ctx.message
                    try:
                        arguments = new_message.content.split(" ", 1)[1]
                    except IndexError:
                        arguments = None
                    new_message.content = (
                        f"{ctx.prefix}{closest_command_name} {arguments}"
                    )

                    await ctx.bot.process_commands(new_message)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                (
                    "You seem to have missed a required argument,"
                    f"check {ctx.prefix}help {ctx.invoked_with}"
                    "for information about how to use it."
                )
            )
        elif isinstance(error, commands.DisabledCommand):
            is_owner = await ctx.bot.is_owner(ctx.message.author)
            if is_owner is True:
                await ctx.command.reinvoke(ctx)
            else:
                await ctx.send(f"The command `{ctx.invoked_with}` has been disabled.")
        elif isinstance(error, discord.Forbidden):
            await ctx.send(
                f"Something went wrong on Discord's side. Sorry for the inconvenience."
            )
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(
                    f"The `{ctx.invoked_with}` cannot be used in Private Messages."
                )
            except discord.Forbidden:
                pass
        else:
            print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )


def setup(bot: commands.Bot):
    bot.add_cog(CommandErrorHandler())
