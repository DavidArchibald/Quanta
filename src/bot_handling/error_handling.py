import traceback
import sys

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

        if hasattr(ctx.command, "on_error"):  # To prevent recursiveness.
            return

        error = getattr(error, "original", error)

        content = ctx.message.content
        prefix = await self.database.get_prefix(ctx)
        command = content.split(" ")[0][len(prefix) :]

        error_message = '"{}" is an unknown command.'.format(command)
        logging_message = None
        logging_traceback = '{author}(id: {author_id}) said "{message}" in the guild {guild}(id: {guild_id}) within the channel {channel}(id: {channel_id})'.format(
            author=ctx.message.author,
            author_id=ctx.message.author.id,
            message=ctx.message.content,
            guild=ctx.message.guild,
            guild_id=ctx.message.guild.id,
            channel=ctx.message.channel,
            channel_id=ctx.message.channel.id,
        )
        if isinstance(error, commands.CommandNotFound):
            pass
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('"{}" has been disabled.'.format(command))
            return
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(
                    '"{}" cannot be used in Private Messages.'.format(command)
                )
                return
            except discord.Forbidden:
                pass

        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )
