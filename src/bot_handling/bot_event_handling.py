import discord
from discord.ext import commands

import traceback
import logging


class BotEventHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        pass

    async def on_ready(self, *args):
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------")

    async def on_error(self, event, *args, **kwargs):
        error = traceback.format_exc()
        logging.warning(error)
        print(error)
