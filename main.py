import discord
from discord.ext import commands
import discord.utils

import GetUserConverter

import time
import sys
import os
import asyncio

import traceback
import logging

myVariable = None
client = discord.Client()
bot = commands.Bot(command_prefix="?")

@client.event
async def on_message(message):
    print(message.content)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

@bot.command()
async def ping(ctx, exact="4"):
    if exact.casefold() == "true" or exact.casefold() == "exact":
        pingTime = bot.latency
    elif exact.isdigit():
        pingTime = round(bot.latency, int(exact))
    else:
        pingTime = round(bot.latency, 4)
    
    await ctx.message.delete()
    await ctx.send("Pong! | {0} seconds".format(pingTime))

@bot.command()
async def say(ctx, *text):
    await ctx.message.delete()
    await ctx.send(" ".join(text))

@bot.command()
@commands.has_role("Quanta's Owner")
async def kill(ctx):
    await ctx.message.delete()
    message = await ctx.send("Goodbye...")
    time.sleep(3)
    await message.delete()
    await bot.logout()

@bot.command()
@commands.has_role("Quanta's Owner")
async def reload(ctx):
    await ctx.message.add_reaction("✅")
    os.execv(sys.executable, ["python"] + sys.argv)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx: commands.context, limit: int=100, user:discord.User="all"):
    """Deletes a number of commands."""
    await ctx.message.delete()
    
    if user.casefold() == "all":
        await ctx.channel.purge(limit=limit)
    
    else:
        #user = async get_user(user)
        def check_user(message):        
            return user == "all" or message.author.name == user
        await ctx.channel.purge(limit=limit, check=check_user)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearAll(ctx):
    await ctx.message.delete()
    confirm=await confirmAction(ctx)
    if not confirm:
        return
    async for message in ctx.channel.history():
        await message.delete()

#@asyncio.coroutine
async def confirmAction(ctx: commands.context, message="Are you sure?"):
    confirm=await ctx.send(message)
    await confirm.add_reaction("✅")
    await confirm.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await confirm.delete()
        #return False

    await confirm.delete()

    if str(reaction.emoji) == "✅":
        return True
    
    return False

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx: commands.context, user: GetUserConverter, reason=""):
    await ctx.kick(user)
    await ctx.send("kicked {0}".format(user))

@bot.command()
async def getMember(ctx: commands.context, user: GetUserConverter="testy"):
    await ctx.send(user.mention)
    pass

@client.event
async def on_error(event, *args, **kwards):
    print("error!")
    message = args[0]
    error = traceback.format_exc()
    logging.warning(error)
    #await discord.Object(id="455870821450383361").send(
    #    "```{0}``` %s".format(error)
    #)

tokenFile = open("token.txt", "r")
token = tokenFile.read()
tokenFile.close()

bot.run(token)
#client.run(token)
