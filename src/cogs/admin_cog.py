#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import asyncio

import discord
from discord.ext import commands

from ..helpers import helper_functions
from ..helpers.helper_functions import GetUserConverter, confirm_action
import re


class AdminCommands:
    """Special commands just for Admins."""

    icon = "<:quantahammer:473960604521201694>"

    def __init__(self, database):
        self.database = database
        self.clearing_channels = []

    @commands.command(usage="purge (count) (user)")
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self, ctx: commands.Context, limit: int = 100, user: GetUserConverter = "all"
    ):
        """Deletes a number of messages by a user.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Keyword Arguments:
            limit {int} -- The max number of messages to purge (default: {100})
            user {GetUserConverter} -- Fuzzy user getting (default: {"all"})
        """

        if user == None or user.casefold() == "all":
            await ctx.channel.purge(limit=limit)

        def check_user(message):
            return user == None or user.casefold() == "all" or message.author == user

        await ctx.channel.purge(limit=limit, check=check_user)

    @commands.command(aliases=["clearall", "clear-all", "clear all"], usage="clearall")
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
        if ctx.channel.id in self.clearing_channels:
            self.clearing_channels.remove(ctx.channel.id)

    @commands.command(usage="kick [user] (reason)")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.context, user: GetUserConverter, reason=""):
        """Kick a user.

        Arguments:
            ctx {commands.context} -- Information about where a command was run.
            user {discord.User} -- Gets a `discord.User` using fuzzy conversion.

        Keyword Arguments:
            reason {str} -- Why the user is being kicked (default: {""})
        """

        await ctx.kick(user)
        await ctx.send(f"kicked {user}")

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
    async def set_prefix(self, ctx: commands.context, *, prefix: str = None):
        """Change the prefix for the channel

        Arguments:
            ctx {commands.context} -- Information about where a command was run.
            prefix {str} -- The prefix to set the guild to use.
        """

        message = None

        current_prefix = await self.database.get_prefix(ctx)
        if prefix == current_prefix:
            await ctx.send(f"Prefix is already set to `{prefix}`!")
            return

        if prefix is None:
            confirm, message = await confirm_action(
                ctx,
                "You may have forgotten the prefix. Do you want to remove the need for a prefix?",
            )
            if not confirm:
                return
            prefix = ""

        if not isinstance(prefix, str):
            prefix = str(prefix)

        prefix_casefold = prefix.casefold()

        boundary_quotes = re.compile(r"^([\"'])(((?!\1).)*)(\1)$")
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
