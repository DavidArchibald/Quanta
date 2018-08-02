#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""A Discord.py bot."""

import discord
from discord.ext import commands
import discord.utils

import traceback
import logging
import logging.handlers

import os
import asyncio

import sys

import yaml

from .helpers import database_helper, helper_functions
from .cogs import general_cog, developer_cog, admin_cog
from .bot_handling import bot_event_handling, error_handling


async def get_prefix_wrapper(bot, message):
    return await database.get_prefix(message.channel)


database = database_helper.Database()
bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix_wrapper)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.connect())

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger("Discord Logger")
    logger.setLevel(logging.INFO)

    log_handler = logging.handlers.RotatingFileHandler(
        "bot.log", maxBytes=10000, backupCount=5
    )
    log_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.WARN)
    stream_handler.setFormatter(stream_handler)

    logger.addHandler(log_handler)
    logger.addHandler(stream_handler)

    config_path = os.path.join(os.path.dirname(__file__), "secrets/config.yaml")

    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)

    bot_info = config["bot_info"]
    token = bot_info["token"]

    bot.remove_command("help")

    helper_commands = helper_functions.HelperCommands()
    developer_commands = developer_cog.DeveloperCommands(database)
    general_commands = general_cog.GeneralCommands(database)
    admin_commands = admin_cog.AdminCommands(database)
    command_error_handler = error_handling.CommandErrorHandler(database)
    bot_event_handler = bot_event_handling.BotEventHandler(bot)

    bot.add_cog(helper_commands)
    bot.add_cog(developer_commands)
    bot.add_cog(general_commands)
    bot.add_cog(admin_commands)
    bot.add_cog(command_error_handler)
    bot.add_cog(bot_event_handler)

    bot.run(token)
