#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import traceback

import discord
from discord.ext import commands


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

        content = ctx.message.content
        prefix = await self.database.get_prefix(ctx)
        command = content.split(" ")[0][len(prefix) :]

        error_message = f'"{command}" is an unknown command.'
        logging_message = None
        logging_traceback = f'{ctx.author}(id: {ctx.author.id}) said "{ctx.message}" in the guild {ctx.guild}(id: {ctx.guild.id}) within the channel {ctx.channel}(id: {ctx.channel.id})'
        if isinstance(error, commands.CommandNotFound):
            pass
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
