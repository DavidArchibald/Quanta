import discord

from typing import Union

DiscordReaction = Union[discord.Reaction, discord.Emoji, discord.PartialEmoji, str]
DiscordUser = Union[discord.abc.User, str]
DiscordChannel = Union[discord.abc.PrivateChannel, discord.abc.GuildChannel]
