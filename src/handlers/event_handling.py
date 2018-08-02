#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands

import logging
import textwrap
import traceback


class BotEventHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        pass

    async def on_ready(self):
        logged_in_message = textwrap.dedent(
            """\
            Logged in as
            {0.name}
            {0.id}
            ------
            """
        ).format(self.bot.user)

        logging.info(logged_in_message)
        print(logged_in_message)

    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        logging.warning(error)
