#!/usr/bin/env python3

import discord
from discord.ext import commands

from typing import Optional

class BotStates:
    def __init__(self: BotStates) -> None:
        self._error_icon: str = ...
    async def error(
        self: BotStates,
        ctx: commands.Context,
        error: Optional[str] = ...,
        source: Optional[str] = ...,
    ):
        sad_error: str = ...
        max_length: int = ...

        error: str = ...
        error_truncated_message: str = ...

        embed: discord.Embed = ...
