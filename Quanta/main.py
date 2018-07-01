"""A Discord.py bot."""

#import asyncio

import traceback
import logging

import discord
from discord.ext import commands
import discord.utils

import helper_functions

#from helper_functions import GetUserConverter
#from helper_functions import HelperCommands
#from helper_functions import get_prefix

import general_commands
import developer_commands
import admin_commands
import error_handling

#from general_commands import GeneralCommands
#from developer_commands import DeveloperCommands
#from admin_commands import AdminCommands
#from error_handling import CommandErrorHandler

client = discord.Client()
bot = commands.Bot(command_prefix=helper_functions.get_prefix)

#@bot.event
#async def on_message(message):
#    print(message.content)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

@bot.event
async def on_error(event, *args, **kwards):
    print("error!")
    #message = args[0]
    error = traceback.format_exc()
    logging.warning(error)
    #await discord.Object(id="455870821450383361").send(
    #    "```{0}``` %s".format(error)
    #)

if __name__ == "__main__": 
    tokenFile = open("token.txt", "r")
    token = tokenFile.read()
    tokenFile.close()

    helperCommands = helper_functions.HelperCommands()
    developerCommands = developer_commands.DeveloperCommands()
    generalCommands = general_commands.GeneralCommands()
    adminCommands = admin_commands.AdminCommands()
    commandErrorHandler = error_handling.CommandErrorHandler()

    bot.add_cog(helperCommands)
    bot.add_cog(developerCommands)
    bot.add_cog(generalCommands)
    bot.add_cog(adminCommands)
    bot.add_cog(commandErrorHandler)

    bot.run(token)
    #client.run(token)
