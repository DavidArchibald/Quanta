"""A Discord.py bot."""

import discord
from discord.ext import commands
import discord.utils

import traceback
import logging

import os

from .helpers import database, helper_functions

from .commands import general_commands, developer_commands, admin_commands
from .bot_handling import error_handling, bot_event_handling

client = discord.Client()
bot = commands.Bot(case_insensitive=True, command_prefix=lambda bot, message: database.get_prefix(message.guild))

if __name__ == "__main__":
    database.connect()

    tokenPath = os.path.join(os.path.dirname(__file__), "secrets/token.txt")
    with open(tokenPath, "r") as tokenFile:
        token = tokenFile.read()

    # bot.remove_command("help")
    # help isn't implemented in this commit, but I've started working on it

    helperCommands = helper_functions.HelperCommands()
    developerCommands = developer_commands.DeveloperCommands()
    generalCommands = general_commands.GeneralCommands()
    adminCommands = admin_commands.AdminCommands()
    commandErrorHandler = error_handling.CommandErrorHandler()
    botEventHandler = bot_event_handling.BotEventHandler(bot)

    bot.add_cog(helperCommands)
    bot.add_cog(developerCommands)
    bot.add_cog(generalCommands)
    bot.add_cog(adminCommands)
    bot.add_cog(commandErrorHandler)
    bot.add_cog(botEventHandler)

    bot.run(token)
    # client.run(token)
