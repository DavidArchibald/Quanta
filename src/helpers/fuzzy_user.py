#!/usr/bin/env python3

import asyncio

import discord
from discord.ext import commands

import fuzzywuzzy
from fuzzywuzzy import process

import itertools
from ..constants import emojis

from . import helper_functions
from .helper_functions import wait_for_reactions

from typing import Union


class FuzzyUser(commands.Converter):
    """Fuzzy user converter

    Arguments:
        commands {commands.Converter} -- Change the type of a variable.

    Returns:
        user {discord.User} -- A discord user if found.
    """

    async def convert(
        self,
        ctx: commands.context,
        identifier: str,
        base_message: discord.Message = None,
    ):
        result_count = 3  # Trim the results to be 3
        # This will only support up to 10 results.
        # A possible fix would be "pages"

        if identifier == None or identifier == "":
            return (identifier, None)

        # Handle escaped usernames
        if identifier.startswith(r"\<@") and identifier.endswith(">"):
            identifier = identifier[1:]

        try:  # Try converting it with the built in UserConverter
            # This will handle exact input in the order:
            # 1. User ID
            # 1. User Mention
            # 2. Username#discriminator
            # 3. Username
            user = await commands.UserConverter().convert(ctx, identifier)
            return (user, None)
        except:
            # Ignore any error it gives out.
            # This is only for efficiency.
            pass

        # If in format <@{user id}> get only the user id.
        if identifier.startswith("<@") and identifier.endswith(">"):
            identifier = identifier[2:-1]

        compares = itertools.chain(
            *[
                filter(None, [str(member.id), member.name, member.nick])
                for member in ctx.guild.members
            ]
        )
        result = process.extract(identifier, compares, limit=result_count)
        result = list(filter(lambda item: item[1] > 50, result))
        result_count = len(result)

        if result_count == 0:
            return (identifier, None)

        # Filtering the result to a reasonable threshold could also help)
        embed = discord.Embed()
        for i, item in enumerate(result):
            identifier = item[0]
            user = await commands.UserConverter().convert(ctx, identifier)
            embed.add_field(
                name=f"{i + 1}. {identifier}", value=user.name, inline=False
            )

        if base_message is not None:
            whom = base_message
            await whom.edit("**Do you mean:**", embed=embed)
        else:
            whom = await ctx.send("**Do you mean:**", embed=embed)
        number_emojis = emojis.number_emojis[1:result_count]

        if result_count == 1:
            reaction = await wait_for_reactions(ctx, whom, (emojis.yes, emojis.no))
            if reaction.emoji == emojis.yes:
                user_identifier = result[0][0]
            else:
                return (identifier, whom)
        else:
            reaction = await wait_for_reactions(ctx, whom, (*number_emojis, emojis.no))
            if reaction == emojis.no:
                return (identifier, whom)

            reaction_number = number_emojis.index(reaction.emoji)
            user_identifier = result[reaction_number][0]

        user = await commands.UserConverter().convert(ctx, user_identifier)
        return (user, whom)

    @staticmethod
    async def handle_no_user(
        ctx: commands.Context,
        user: Union[discord.User, discord.Member, str],
        message: discord.Message,
        no_user_message: str = None,
    ):
        if isinstance(user, str):
            no_user_message = no_user_message or f'Couldn\'t find the user "{user}".'
            if message is None:
                await ctx.send(content=no_user_message)
            else:
                await message.edit(content=no_user_message, embed=None)
            return None

        return user


class GetUser:
    @commands.command(
        usage="getuser [user]",
        aliases=["getuser", "get-user", "get_member", "getmember", "get-member"],
    )
    async def get_user(self, ctx: commands.Context, fuzzy_user: FuzzyUser):
        user, message = fuzzy_user
        response = await FuzzyUser.handle_no_user(ctx, user, message)
        if response == None:
            return

        content = user.mention
        if message is None:
            await ctx.send(content=content)
        else:
            await message.edit(content=content, embed=None)


def setup(bot, database):
    bot.add_cog(GetUser())
