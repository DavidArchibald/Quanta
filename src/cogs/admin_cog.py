#!/usr/bin/env python3

import discord
from discord.ext import commands

import asyncio
import re

from ..helpers.helper_functions import confirm_action
from ..helpers.fuzzy_user import FuzzyUser
from ..helpers.database_helper import Database

from typing import Union, List


class AdminCommands:
    """Special commands just for Admins."""

    icon = "<:quantahammer:473960604521201694>"

    def __init__(self, database: Database) -> None:
        self.database: Database = database
        self.clearing_channels: List[discord.TextChannel] = []

    @commands.command(usage="purge (count) (user)")
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self, ctx, limit: int = 100, fuzzy_user: Union[FuzzyUser, str] = "all"
    ):
        """Deletes a number of messages by a user.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Keyword Arguments:
            limit {int} -- The max number of messages to purge (default: {100})
            fuzzy_user {FuzzyUser} -- Fuzzy user getting (default: {"all"})
        """

        if fuzzy_user == None or (
            isinstance(fuzzy_user, str) and fuzzy_user.casefold() == "all"
        ):
            await ctx.channel.purge(limit=limit)
            return

        user, _ = fuzzy_user

        def check_user(message: discord.Message) -> bool:
            return (
                user == None
                or message.author == user
                or (isinstance(user, str) and user.casefold() == "all")
            )

        await ctx.channel.purge(limit=limit, check=check_user)

    @commands.command(aliases=["clearall", "clear-all"], usage="clearall")
    @commands.cooldown(
        1, 86400, commands.BucketType.user
    )  # So one person can't abuse the feature.
    @commands.cooldown(
        1, 86400, commands.BucketType.channel
    )  # Only allows this to be used once a day in a channel.
    @commands.has_permissions(manage_messages=True)
    async def clear_all(self, ctx: commands.Context):
        """Remove all messsages.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """
        deleted_message = 0

        confirm, confirm_message = await confirm_action(
            ctx, message="Are you sure you want to delete all these messages?"
        )

        if not confirm:
            await confirm_message.edit(content="Clearing messages cancelled")
            return

        prefix = await self.database.get_prefix(ctx)
        await confirm_message.edit(
            content=f"Deleting messages... Stop with {prefix}stopclearing"
        )
        self.clearing_channels.append(ctx.channel.id)

        async for message in ctx.channel.history(limit=None):
            if ctx.channel.id not in self.clearing_channels:
                break
            if message.id != confirm_message.id:
                await message.delete()
                deleted_message += 1

        await confirm_message.delete()
        await ctx.send(content=f"Deleted {deleted_message} messages")

    @commands.command(usage="stopclearing", aliases=["stopclearing", "stop-clearing"])
    @commands.cooldown(
        1, 86400, commands.BucketType.channel
    )  # Only allow this to be used once a day in a channel.
    @commands.has_permissions(manage_messages=True)
    async def stop_clearing(self, ctx: commands.Context):
        """Stops `clear_all` from removing all the message.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        if ctx.channel.id in self.clearing_channels:
            self.clearing_channels.remove(ctx.channel.id)

    @commands.command(usage="kick [user] (reason)")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: FuzzyUser, reason: str = ""):
        """Kick a user.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            user {FuzzyUser} -- Gets a `discord.User` using fuzzy conversion.

        Keyword Arguments:
            reason {str} -- Why the user is being kicked (default: {""})
        """
        for_reason = f"For {reason}" if reason is not None and reason != "" else ""

        try:
            await ctx.kick(user)
        except discord.HTTPException:
            await ctx.send(f"Could not kick user {user}!")
            return

        if not user.is_blocked():
            try:
                await user.send(
                    f"You were kicked from the server {ctx.server} for {for_reason}."
                )
            except discord.HTTPException:
                pass

        await ctx.send(f"Kicked {user} for {for_reason}.")

    @commands.command(
        aliases=[
            "setprefix",
            "set-prefix",
            "changeprefix",
            "change_prefix",
            "change-prefix",
        ],
        usage="setprefix [prefix]",
    )
    @commands.has_permissions(manage_channels=True)
    async def set_prefix(self, ctx: commands.Context, *, prefix: str = None):
        """Change the prefix for the channel

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            prefix {str} -- The prefix to set the guild to use.
        """

        confirm = None
        message = None
        no_change_message = "Prefix has not been changed."

        current_prefix = await self.database.get_prefix(ctx)
        if prefix == current_prefix:
            await ctx.send(f"The prefix is already set to `{prefix}`!")
            return

        if prefix is None:
            confirm, message = await confirm_action(
                ctx,
                "You may have forgotten the prefix. Do you want to remove the need for a prefix?",
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return
            prefix = ""

        if not isinstance(prefix, str):
            prefix = str(prefix)

        has_reference = re.compile(
            r"(<@(?:!?|&|#)\d+>)"
        )  # Checks if the string has a user or role mention or a channel "reference".
        references = re.findall(has_reference, prefix)
        if references is not None or "@everyone" in prefix or "@here" in prefix:
            # References have a zero width joiner to doubly prevent mentions
            raw_bot_mention = f"<@{ctx.bot.user.id}>"
            bot_mention = ctx.bot.user.mention
            if prefix == raw_bot_mention:
                await ctx.send(
                    f"I already respond to {bot_mention}. No need to set it to the prefix."
                )
            elif raw_bot_mention in references:
                await ctx.send(
                    f"I already respond to {bot_mention}, adding extra characters just makes it confusing."
                )
            else:
                await ctx.send(
                    f'You can\'t include "references" such as @user, #‍channel, @‍everyone, or @‍here in your prefix, sorry.'
                )
            return

        prefix_casefold = prefix.casefold()

        boundary_quotes = re.compile(r"^([\"'])((((?!\1).)|\\\1)*)(\1)$")
        match = boundary_quotes.match(prefix)
        while match:  # Removes wrapped quotes ie 'lorem', "ipsum" "'dolor'" '"sit"'
            prefix = prefix[1:-1]
            match = boundary_quotes.match(prefix)
            prefix_casefold = prefix.casefold()

        if len(prefix) > 32:
            await ctx.send(f"Your prefix can't be greater than 32 characters, sorry!")
            return
        elif len(prefix) > 10:
            confirm, message = await confirm_action(
                ctx,
                f'Your prefix is pretty long. Are you sure you want to set it to "{prefix}"?',
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return

        if "'" in prefix_casefold or '"' in prefix_casefold:
            await ctx.send(
                f"Quotes can mess with how I parses arguments, so you can't use quotes in your prefix, sorry!"
            )
            return

        markdown = ("*", "\\", "__", "~~", "`")
        if any(character in prefix_casefold for character in markdown):
            confirm, message = await confirm_action(
                ctx,
                f'Markdown can be annoying! Are you sure you want to set the prefix to "{prefix}"? It may format stuff in unexpected ways.',
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return

        try:
            await self.database.set_prefix(ctx, prefix)
        except Exception:
            unexpected_exception = "An unexpected Exception occurred."
            if message is not None:
                await message.edit(content=unexpected_exception)
            else:
                await ctx.send(unexpected_exception)
            return

        prefix_set = f'The prefix has been set to: "{prefix}" successfully!'
        if message is not None:
            await message.edit(content=prefix_set)
        else:
            await ctx.send(prefix_set)

    # @commands.command(usage="load [cog]")
    # async def load(ctx, )


def setup(bot, database):
    bot.add_cog(AdminCommands(database))
