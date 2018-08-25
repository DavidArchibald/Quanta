#!/usr/bin/env python3

import asyncio

import discord
from discord.ext import commands

from typing import Union, Mapping, Optional, Mapping, Tuple, List

from .database_helper import Database

class HelperCommands:
    async def error(self: HelperCommands, ctx: commands.Context): ...
    async def wait(self: HelperCommands, ctx: commands.Context, time: int = ...):
        message: discord.Message = ...
    async def unusable(self: HelperCommands, ctx: commands.Context):
        is_owner: bool = ...

async def confirm_action(
    ctx: commands.Context,
    message: Union[str, discord.Embed, Mapping[str, discord.Embed]] = "Are you sure?",
    base_message: Optional[discord.Message] = ...,
    timeout: float = ...,
) -> Tuple[bool, discord.Message]:
    embed: Optional[discord.Embed] = ...
    message: discord.Message = ...

    confirm: discord.Message = base_message.edit(content=message, embed=embed)

async def wait_for_reactions(
    ctx: commands.Context,
    message: discord.Message,
    reactions: Union[discord.Reaction, discord.Emoji, discord.PartialEmoji, str],
    timeout: int = 60.0,
    timeout_message: Union[
        str, discord.Embed, Mapping[str, discord.Embed]
    ] = "Timed out!",
    remove_reactions: bool = True,
    remove_reactions_on_timeout: bool = None,
) -> discord.Reaction:

    reaction: Optional[discord.Reaction] = ...
    user: Optional[discord.User, discord.message] = ...

def escape_markdown(text: str) -> str:
    markdown_characters: List[str] = ...

def setup(bot: commands.bot, database: Database): ...
