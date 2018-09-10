import discord

from typing import Union

DiscordReaction = Union[discord.Reaction, discord.Emoji, discord.PartialEmoji, str]
DiscordUser = Union[discord.Member, discord.User, str]
