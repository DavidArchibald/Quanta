#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import asyncio

import discord
from discord.ext import commands

from ..helpers import helper_functions
from ..helpers.helper_functions import GetUserConverter, confirm_action


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
        await ctx.send("kicked {0}".format(user))

    @commands.command(
        aliases=[
            "setprefix",
            "set-prefix",
            "set prefix",
            "changeprefix",
            "change_prefix",
            "change-prefix",
            "change prefix",
        ],
        usage="setprefix [prefix]",
    )
    @commands.has_permissions(manage_channels=True)
    async def set_prefix(self, ctx: commands.context, prefix: str):
        """Change the prefix for the channel

        Arguments:
            ctx {commands.context} -- Information about where a command was run.
            prefix {str} -- The prefix to set the guild to use.
        """

        if prefix == "":
            if ctx.prefix == "":
                await ctx.send("This channel already has no prefix.")
            else:
                await confirm_action(
                    ctx,
                    "Are you sure you want to set the prefix to none in this channel?",
                )
            return

        await self.database.set_prefix(ctx, prefix)
