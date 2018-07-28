"""A Discord.py bot."""

import discord
from discord.ext import commands
import discord.utils

import traceback
import logging

import os
import sys

import asyncio

import yaml

from .helpers import database_helper, helper_functions
from .commands import general_commands, developer_commands, admin_commands
from .bot_handling import error_handling, bot_event_handling

async def _get_prefix(bot, message):
    prefix = await database.get_prefix(message.channel)
    return prefix

database = database_helper.Database()
bot = commands.Bot(case_insensitive=True, command_prefix=_get_prefix)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.connect())

    #bot.loop.set_debug(True)
    config_path = os.path.join(os.path.dirname(__file__), "secrets/config.yaml")

    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    
    bot_info = config["bot_info"]
    token = bot_info["token"]
    
    bot.remove_command("help")

    helper_commands = helper_functions.HelperCommands()
    developer_commands = developer_commands.DeveloperCommands(database)
    general_commands = general_commands.GeneralCommands(database)
    admin_commands = admin_commands.AdminCommands(database)
    command_error_handler = error_handling.CommandErrorHandler(database)
    bot_event_handler = bot_event_handling.BotEventHandler(bot)

    bot.add_cog(helper_commands)
    bot.add_cog(developer_commands)
    bot.add_cog(general_commands)
    bot.add_cog(admin_commands)
    bot.add_cog(command_error_handler)
    bot.add_cog(bot_event_handler)

    bot.run(token)
