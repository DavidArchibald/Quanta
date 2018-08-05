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
    @commands.has_permissions(manage_messages=True)
    async def clear_all(self, ctx: commands.Context):
        """Remove all messsages.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """

        confirm = await confirm_action(ctx)

        if not confirm:
            return

        async for message in ctx.channel.history(limit=None):
            await message.delete()

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
            "change prefix",
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

        if prefix is None:
            confirm = await confirm_action(
                ctx, "Are you sure you want to remove the need for a prefix?"
            )
            if not confirm:
                return
            prefix = ""

        if not isinstance(prefix, str):
            return

        boundary_quotes = re.compile(r"^([\"'])(((?!\1).)*)(\1)$")
        match = boundary_quotes.match(prefix)
        while match:  # Removes wrapped quotes ie 'lorem', "ipsum" "'dolor'" '"sit"'
            prefix = prefix[1:-1]
            match = boundary_quotes.match(prefix)

        if prefix.casefold().contains(("'", '"')):
            confirm = await confirm_action(
                ctx,
                f"Quotes can mess with how the bot parses arguments, so please don't use quotes in your prefix.",
            )
            return

        if prefix.casefold().contains(("*", "\\", "__", "~~", "`")):
            confirm = await confirm_action(
                ctx,
                f"Markdown can be annoying! Are you sure you want to set the prefix to {prefix}? It may format commands in unexpected ways.",
            )
            if not confirm:
                return

        if prefix == ctx.prefix:
            await ctx.send(f"Prefix is already set to `{prefix}`!")
            return

        try:
            await self.database.set_prefix(ctx, prefix)
        except Exception:
            await ctx.send(f"An unexpected Exception occurred.")
            return

        await ctx.send(f"The prefix has been set to `{prefix}` successfully!")
