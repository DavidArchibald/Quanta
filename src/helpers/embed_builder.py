#!/usr/bin/env python3

import discord
from discord.ext import commands

import random

from ..globals.embed_builder import sad_errors

from typing import Optional, Union

# TODO: Implement trimming better.


class EmbedBuilder:
    """Build's messages based upon different "states" the bot can be in."""

    def __init__(self) -> None:
        self._error_icon = "<:quantaerror:475409387863670810>"
        self._fail_icon = "<:quantax:475032169086058496>"
        self._success_icon = "<:quantacheck:475029940639891467>"
        self._max_length = {
            "field": 25,
            "title": 256,
            "field_name": 256,
            "value": 1024,
            "footer": 2048,
            "description": 2048,
            "all": 6000,
        }

    def error(
        self,
        error: Optional[Union[str, BaseException]] = None,
        source: str = None,
        trim=True,
    ):
        """Sends an embed based upon an error.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.

        Keyword Arguments:
            error {Union[str, BaseException]} -- The error to display. (default: {None})
            source {str} -- Where the error came from. (default: {None})
            trim {bool} -- Whether to trim the content or not. (default: {True})
        """

        sad_error = random.choice(sad_errors)
        if error is None:
            error = "An unknown error occurred."

        if isinstance(error, BaseException):
            # Gets the traceback, possibly truncated

            error = str(error)
            if len(error) > self._max_length["description"]:
                if trim is False:
                    raise RuntimeError(
                        (
                            "The message must be trimmed, "
                            "but the argument trim has been set to False. "
                            "Either use a paginator or allow trimming."
                        )
                    )
                error_truncated_message = "\n**---Error Truncated---**"
                error = (
                    error[
                        : self._max_length["description"] - len(error_truncated_message)
                    ]
                    + error_truncated_message
                )

        embed = discord.Embed(
            title=f"{self._error_icon} {sad_error}",
            description=f"**{error}**",
            colour=0xcc0000,
        )

        return embed

    def success(self, title, description, footer=None, trim=True):
        """Sends an embed based upon a successful scenario.

        Arguments:
            title {str} -- The embed's title.
            description {str} -- The embed's content.

        Keyword Arguments:
            trim {bool} -- Whether to trim the content or not. (default: {True})

        Raises:
            RuntimeError -- If the content cannot be trimmed.

        Returns:
            discord.Embed -- The resulting embed.
        """

        max_title_length = self._max_length["title"] - 2
        if len(title) > max_title_length:
            if trim is False:
                raise RuntimeError(
                    (
                        "The message must be trimmed, "
                        "but the argument trim has been set to False. "
                        "Either use a paginator or allow trimming."
                    )
                )
            title = title[:max_title_length]

        embed = discord.Embed(
            title=f"{self._success_icon} {title}",
            description=f"{description}",
            colour=0x00ff00,
        )

        if footer is not None and footer != "":
            embed.set_footer(text=footer)

        return embed

    def fail(self, title, description, trim=True):
        """Sends an embed based upon a failing scenario.

        Arguments:
            title {str} -- The embed's title.
            description {str} -- The embed's description.

        Keyword Arguments:
            trim {bool} -- Whether to trim the content or not. (default: {True})

        Raises:
            RuntimeError -- If the content cannot be trimmed.

        Returns:
            discord.Embed -- The resulting embed.
        """

        max_title_length = self._max_length["title"] - 2
        if len(title) > max_title_length:
            if trim is False:
                raise RuntimeError(
                    (
                        "The message must be trimmed, "
                        "but the argument trim has been set to False. "
                        "Either use a paginator or allow trimming."
                    )
                )
            title = title[:max_title_length]

        embed = discord.Embed(
            title=f"{self._fail_icon} {title}",
            description=f"{description}",
            colour=0x00ff00,
        )

        return embed

    async def default(self, ctx: commands.Context, title: str, content: str, trim=True):
        if len(content) + len(title) > 2000:
            if trim is False:
                raise RuntimeError("The content is too long.")

        embed = discord.Embed(title=title, description=content, colour=0x0000ff)
        return embed
