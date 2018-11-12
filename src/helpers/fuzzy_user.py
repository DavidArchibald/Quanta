#!/usr/bin/env python3

import discord
from discord.ext import commands

from fuzzywuzzy import process

from ..globals import emojis
from ..globals.custom_types import DiscordUser

from .helper_functions import wait_for_reactions

from typing import Tuple, Optional


class FuzzyUser(commands.Converter):
    """Fuzzy user converter

    Arguments:
        commands {commands.Converter} -- Change the type of a variable.

    Returns:
        user {discord.User} -- A discord user if found.
    """

    async def convert(
        self,
        ctx: commands.Context,
        identifier: str,
        base_message: discord.Message = None,
    ) -> Tuple[Optional[DiscordUser], Optional[discord.Message]]:
        result_count = 3  # Trim the results to be 3
        # This will only support up to 10 results.
        # A possible fix would be "pages"

        if identifier is None or identifier == "":
            return (identifier, None)

        # Handle escaped usernames
        if identifier.startswith(r"\<@") and identifier.endswith(">"):
            identifier = identifier[1:]

        try:
            # Try converting it with the built in UserConverter
            # This will handle exact input in the order:
            # 1. User ID
            # 2. User Mention
            # 3. Username#discriminator
            # 4. Username
            user = await commands.UserConverter().convert(ctx, identifier)
            return (user, None)
        except commands.BadArgument:
            pass

        # If in format <@{user id}> get only the user id.
        if identifier.startswith("<@") and identifier.endswith(">"):
            identifier = identifier[2:-1]

        # Compiles a list of ids, names, and nicknames
        compares = [
            name
            for member in ctx.guild.members
            for name in (str(member.id), member.name, member.nick)
            if name is not None
        ]
        results = process.extract(identifier, compares, limit=result_count)
        results = [result for result in results if result[1] > 5]
        result_count = len(results)  # may be less than the max.

        if results is None:
            return (identifier, None)

        # Filtering the result to a reasonable threshold could also help)
        embed = discord.Embed()
        for i, item in enumerate(results):
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
            if reaction is None:
                return (identifier, None)
            elif reaction.emoji == emojis.yes:
                user_identifier = results[0][0]
            else:
                return (identifier, whom)
        else:
            reaction = await wait_for_reactions(ctx, whom, (*number_emojis, emojis.no))
            if reaction is None or reaction == emojis.no:
                return (identifier, None)

            reaction_number = number_emojis.index(reaction.emoji)
            user_identifier = results[reaction_number][0]

        user = await commands.UserConverter().convert(ctx, user_identifier)
        return (user, whom)

    @staticmethod
    async def handle_no_user(
        ctx: commands.Context,
        user: DiscordUser,
        message: discord.Message,
        no_user_message: str = None,
    ) -> DiscordUser:
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
        name="GetUser",
        usage="getuser [user]",
        aliases=["get-user", "get_member", "getmember", "get-member"],
    )
    @commands.guild_only()
    async def get_user(self, ctx: commands.Context, fuzzy_user: FuzzyUser):
        """Gets a user using a member string and fuzzy checking.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            fuzzy_user {FuzzyUser} -- Gets a user using a string with a user's name.
        """

        user, message = fuzzy_user
        response = await FuzzyUser.handle_no_user(ctx, user, message)
        if response is None:
            return

        content = user.mention
        if message is None:
            await ctx.send(content=content)
        else:
            await message.edit(content=content, embed=None)


def setup(bot: commands.Bot):
    bot.add_cog(GetUser())
