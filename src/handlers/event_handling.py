#!/usr/bin/env python3

import datetime
import logging
import textwrap
import traceback

import discord
from discord.ext import commands

from ..globals import emojis, variables


class BotEventHandler:
    """Handles various bot events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    async def on_ready(self):
        self.bot.launch_time = datetime.datetime.now()

        emojis.get_emojis(self.bot)
        logged_in_message = textwrap.dedent(
            f"""\
            Logged in as
            {self.bot.user.name}
            {self.bot.user.id}
            ------
            """
        )

        logging.info(logged_in_message)
        print(logged_in_message)

        await self.bot.change_presence(
            status=discord.Status.online, activity=discord.Game(name="?help")
        )

        variables.is_ready = True

    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        logging.warning(error)


def setup(bot: commands.Bot):
    bot_event_handler = BotEventHandler(bot)

    bot.add_cog(bot_event_handler)
