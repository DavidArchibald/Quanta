#!/usr/bin/env python3

import discord
from discord.ext import commands

import traceback


class BotStates:
    """Sends messages about the bot's state."""

    def __init__(self):
        self._error_icon = "<:quantaerror:475409387863670810>"

    async def error(self, ctx: commands.Context, error: str = None, source: str = None):
        if error is None:
            error = "An unknown error occurred."

        if isinstance(error, BaseException):
            # Gets the traceback truncated
            try:
                # `raise error from None` makes it only print the latest traceback
                raise error from None  # pylint: disable-msg=E0702
            except BaseException:
                error = traceback.format_exc()

            if len(error) >= 100:
                error_truncated_message = "\n**---Error Truncated---**"
                # Discord should interpret this as being 22 characters.
                # and len doesn't really work because of markdown parsing
                error_truncated_length = 22
                error = error[: 100 - error_truncated_length] + error_truncated_message

        embed = discord.Embed(
            title=f"{self._error_icon} An error occurred!",
            description=f"**{error}**",
            colour=0xcc0000,
        )

        await ctx.send(embed=embed)
