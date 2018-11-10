#!/usr/bin/env python3

import discord
from discord.ext import commands

import re

import logging
import traceback

from ..helpers.helper_functions import confirm_action
from ..helpers.fuzzy_user import FuzzyUser

from ..globals import variables

from typing import Union, List


class AdminCommands:
    """Special commands just for Admins."""

    icon = "<:quantahammer:473960604521201694>"

    def __init__(self) -> None:
        self.clearing_channels: List[discord.TextChannel] = []

    @commands.command(name="Purge", usage="purge (count) (user)")
    @commands.guild_only()
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

        if fuzzy_user is None or (
            isinstance(fuzzy_user, str) and fuzzy_user.casefold() == "all"
        ):
            await ctx.channel.purge(limit=limit)
            return

        user, _ = fuzzy_user

        def check_user(message: discord.Message) -> bool:
            return (
                user is None
                or message.author == user
                or (isinstance(user, str) and user.casefold() == "all")
            )

        await ctx.channel.purge(limit=limit, check=check_user)

    @commands.command(name="ClearAll", aliases=["clear-all"], usage="clearall")
    @commands.guild_only()
    # The command is only able to be used once per channel and once per user every day.
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.cooldown(1, 86400, commands.BucketType.channel)
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

        await confirm_message.edit(
            content=f"Deleting messages... Stop with {ctx.invoked_with}"
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

    @commands.command(
        name="StopClearing", usage="stopclearing", aliases=["stop-clearing"]
    )
    # The command is only able to be used once per channel.
    # It is intentional that an individual user can cancel unlimited.
    @commands.cooldown(1, 86400, commands.BucketType.channel)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def stop_clearing(self, ctx: commands.Context):
        """Stops `clear_all` from removing all the message.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        if ctx.channel.id in self.clearing_channels:
            self.clearing_channels.remove(ctx.channel.id)

    @commands.command(name="Kick", usage="kick [user] (reason)")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: FuzzyUser, reason: str = ""):
        """Kick a user.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            user {FuzzyUser} -- Gets a `discord.User` using fuzzy conversion.

        Keyword Arguments:
            reason {str} -- Why the user is being kicked (default: {""})
        """
        for_reason = f" for {reason}" if reason != "" else ""

        try:
            await ctx.kick(user)
        except discord.HTTPException:
            await ctx.send(f"Could not kick user {user}!")
            return

        if user.is_blocked() is False:
            try:
                await user.send(
                    f"You were kicked from the server {ctx.server} for {for_reason}."
                )
            except discord.HTTPException:
                pass

        await ctx.send(f"Kicked {user}{for_reason}.")

    @commands.command(
        name="SetPrefix",
        aliases=["set-prefix", "changeprefix", "change_prefix", "change-prefix"],
        usage="setprefix [prefix]",
    )
    @commands.has_permissions(manage_channels=True)
    async def set_prefix(self, ctx: commands.Context, *, prefix: str = None):
        """Change the prefix for the channel

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
            prefix {str} -- The prefix to set the guild to use.
        """

        if not variables.database.is_connected:
            await ctx.send(
                "You can't change the prefix right now: the database is closed."
            )
            return

        confirm = None
        message = None
        no_change_message = "The prefix has not been changed."

        current_prefix = await variables.database.get_prefix(ctx)
        if prefix == current_prefix:
            await ctx.send(f"The prefix is already set to `{prefix}`!")
            return

        if prefix is None:
            confirm, message = await confirm_action(
                ctx, "You haven't supplied a prefix, do you want to remove the prefix?"
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return
            prefix = ""

        # Checks if the string has a user or role mention or a channel.
        # This will be collectively called "references".
        has_reference = re.compile(r"(<@(?:!?|&|#)\d+>)")
        references = re.findall(has_reference, prefix)
        if references not in ([], None) or "@everyone" in prefix or "@here" in prefix:
            raw_bot_mention = f"<@{ctx.bot.user.id}>"
            bot_mention = ctx.bot.user.mention
            if prefix == raw_bot_mention:
                await ctx.send(
                    (
                        f"I already respond to {bot_mention}. "
                        "No need to set it to the prefix."
                    )
                )
            elif raw_bot_mention in references:
                await ctx.send(
                    (
                        f"I already respond to {bot_mention}, "
                        "adding extra characters just makes it confusing."
                    )
                )
            else:
                # \u200d is a zero width joiner
                # This prevents them from being valid references,
                # while appearing like they are.
                await ctx.send(
                    (
                        'You can\'t include "references" such as '
                        "@\u200duser, #\u200dchannel, @\u200deveryone, or @\u200dhere "
                        "in your prefix, sorry."
                    )
                )
            return

        # Removes wrapped quotes ie 'lorem', "ipsum". "'dolor'", and '"sit"'
        boundary_quotes = re.compile(r"^([\"'])((((?!\1).)|\\\1)*)(\1)$")
        match = boundary_quotes.match(prefix)
        while match:
            prefix = prefix[1:-1]
            match = boundary_quotes.match(prefix)

        if len(prefix) > 32:
            await ctx.send(f"Sorry, your prefix can't be greater than 32 characters.")
            return
        elif len(prefix) > 10:
            confirm, message = await confirm_action(
                ctx,
                (
                    "Your prefix is pretty long."
                    f'Are you sure you want to set it to "{prefix}"?'
                ),
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return

        if "'" in prefix or '"' in prefix:
            await ctx.send(
                (
                    "Sorry, quotes can mess with how I parses arguments, "
                    "so you can't use quotes in your prefix."
                )
            )
            return

        markdown = ("*", "\\", "__", "~~", "`")
        if any(character in prefix for character in markdown):
            confirm, message = await confirm_action(
                ctx,
                (
                    "Markdown can be annoying! "
                    f'Are you sure you want to set the prefix to "{prefix}"? '
                    "It may format stuff in unexpected ways and "
                    "make it harder to replicate."
                ),
            )
            if not confirm:
                await message.edit(content=no_change_message)
                return

        try:
            await variables.database.set_prefix(ctx, prefix)
        except RuntimeError:
            database_closed = "The database has unexpectedly closed."
            if message is not None:
                await message.edit(content=database_closed)
            else:
                await ctx.send(database_closed)
            return
        except BaseException:
            unexpected_exception = "An unexpected exception occurred."
            logging.warning(traceback.format_exc())
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

    # @commands.command(name="Load", usage="load [cog]")
    # async def load(ctx, )


def setup(bot):
    bot.add_cog(AdminCommands())
