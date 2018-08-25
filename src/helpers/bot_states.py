#!/usr/bin/env python3

import discord
from discord.ext import commands

import random
import traceback

from ..constants import bot_states
from ..constants.bot_states import sad_errors


class BotStates:
    """Sends messages about the bot's state."""

    def __init__(self) -> None:
        self._error_icon = "<:quantaerror:475409387863670810>"

    async def error(self, ctx: commands.Context, error: str = None, source: str = None):
        sad_error = random.choice(sad_errors)
        max_length = 2000 - len(sad_error) - 6
        if error is None:
            error = "An unknown error occurred."

        if isinstance(error, BaseException):
            # Gets the traceback truncated

            error = str(error)
            if len(error) >= max_length:
                error_truncated_message = "\n**---Error Truncated---**"
                error = (
                    error[: max_length - len(error_truncated_message)]
                    + error_truncated_message
                )

        embed = discord.Embed(
            title=f"{self._error_icon} {sad_error}",
            description=f"**{error}**",
            colour=0xcc0000,
        )

        await ctx.send(embed=embed)
