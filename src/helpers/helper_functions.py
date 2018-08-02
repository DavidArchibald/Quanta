import discord
from discord.ext import commands

import asyncio
import re

import operator

from .get_user_converter import GetUserConverter
import asyncio


class HelperCommands:
    # Helper Commands is currently exposed for testing purposes.

    @commands.command(aliases=["getmember", "get-member"], usage="getmember [user]")
    async def get_member(self, ctx: commands.context, user: GetUserConverter):
        """Mainly to test GetUserConverter

        Arguments:
            ctx {commands.context} -- Information about where the command was run.

        Keyword Arguments:
            user {GetUserConverter} -- Gets the user
        """

        await ctx.send(user.mention)

    @commands.command(aliases=["getemoji", "get-emoji"], usage="getemoji [emoji]")
    async def get_emoji(self, ctx: commands.context, *emoji: str):
        """Get an emoji and display it.

        Arguments:
            ctx {commands.context} -- Information about where the command was run.
            *emoji {str} -- Get the message
        """

        await ctx.send(ctx.bot.emojis)
        await ctx.send(discord.utils.get(ctx.bot.get_all_emojis(), name=emoji))


async def confirm_action(ctx: commands.context, message="Are you sure?"):
    confirm = await ctx.send(message)
    await confirm.add_reaction("✅")
    await confirm.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in ["✅", "❌"]

    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add", timeout=15.0, check=check
            )
        except asyncio.TimeoutError:
            await confirm.delete()
            return False

        try:
            await confirm.remove_reaction(reaction, user)
        except discord.HTTPException:
            pass

    await confirm.delete()

    if str(reaction.emoji) == "✅":
        return True

    return False


def smallest(a: str, b: str):
    ab, ba = a + b, b + a
    if ab == ba:
        return 0
    if ab < ba:
        return -1
    return 1
