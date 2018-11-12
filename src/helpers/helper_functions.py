#!/usr/bin/env python3

import asyncio

import discord
from discord.ext import commands

from typing import Union, List, Tuple, Optional

from .embed_builder import EmbedBuilder
from ..globals import emojis
from ..globals.custom_types import DiscordReaction, DiscordChannel


build_embed = EmbedBuilder()


class HelperCommands:
    # Helper Commands are exposed for testing purposes.
    @commands.command(name="Error", usage="error [error]")
    async def error(self, ctx: commands.Context):
        """Simulates error catching for testing.

        Arguments:
            ctx {commands.Context} -- Information about where a command was run.
        """

        try:
            1 / 0
        except ZeroDivisionError as exception:
            await build_embed.error(ctx, exception)

    @commands.command(name="Wait", usage="wait [time]")
    @commands.is_owner()
    async def wait(self, ctx: commands.Context, time: int = 1):
        """Waits for a while. Mostly for testing kill.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Keyword Arguments:
            time {int} -- How long to wait in seconds. (default: {1})
        """

        message = await ctx.send("Waiting...")

        await message.add_reaction(emojis.loading)
        await asyncio.sleep(time)

        await message.edit(content="Finished Waiting.")
        await message.remove_reaction(emojis.loading, ctx.bot.user)
        await message.add_reaction(emojis.yes)

    @commands.command(name="Unusable", usage="unusable")
    @commands.check(lambda _: False)
    async def unusable(self, ctx: commands.Context):
        """Used for testing the Sudo command or owner overrides... or commands.check glitches

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.
        """
        is_owner = await ctx.bot.is_owner(ctx.message.author)

        if is_owner is True:
            await ctx.send("Hey owner!")
        else:
            await ctx.send("This is supposed to be unusable... How're you using this?")

    @commands.command(name="GetReaction", usage="getreaction")
    async def get_reaction(self, ctx: commands.Context):
        message = await ctx.send("React with the reaction you want info on.")
        reaction = await wait_for_reactions(ctx, message)
        print(reaction.emoji.encode("unicode_escape"))
        title = (
            reaction.emoji.name
            if isinstance(reaction.emoji, discord.Emoji)
            else reaction.emoji
        )
        embed = discord.Embed(title=f"Reaction Info: {title}", colour=0x0000FF)
        if isinstance(reaction.emoji, discord.Emoji):
            embed.add_field(name="id", value=reaction.emoji.id)

        await message.remove_reaction(reaction, ctx.bot.user)
        await message.edit(embed=embed)

    @commands.group()
    async def lorem(self, ctx: commands.Context):
        ...

    @lorem.group()
    async def ipsum(self, ctx: commands.Context):
        ...

    @ipsum.group()
    async def dolor(self, ctx: commands.Context):
        ...

    @dolor.group()
    async def sit(self, ctx: commands.Context):
        ...

    @sit.command()
    async def amet(self, ctx: commands.Context):
        ...


async def confirm_action(
    ctx: commands.Context,
    message: Union[
        str, discord.Embed, Tuple[str, discord.Embed], List
    ] = "Are you sure?",
    base_message: discord.Message = None,
    timeout: float = 60.0,
) -> tuple:
    """Checks if you're sure you want to continue.

    Arguments:
        ctx {commands.Context} -- Information about where the command was run.

    Keyword Arguments:
        message {str} -- What it asks you about. (default: {"Are you sure?"})
        base_message {commands.Message} -- The message to use. (default: {None})
        timeout {float} -- How long to wait until canceling. (default: {60.0})

    Returns:
        (bool, commands.Message) -- The result and the message used to ask confirmation.
    """
    embed = None
    if isinstance(message, (list, tuple)):
        embed = message[1]
        message = message[0]

    if base_message is not None:
        confirm = base_message.edit(content=message, embed=embed)
    else:
        try:
            confirm = await ctx.send(content=message, embed=embed)
        except discord.HTTPException:
            return (False, confirm)

    reaction = await wait_for_reactions(ctx, confirm, (emojis.yes, emojis.no))

    if reaction is not None and reaction.emoji == emojis.yes:
        return (True, confirm)

    return (False, confirm)


async def wait_for_reactions(
    ctx: commands.Context,
    message: discord.Message,
    reactions: Optional[Union[List[DiscordReaction], Tuple]] = None,
    timeout: Union[int, float] = 60.0,
    timeout_message: Union[
        str, discord.Embed, Tuple[str, discord.Embed], List
    ] = "Timed out!",
    remove_reactions: bool = True,
    remove_reactions_on_timeout: bool = None,
) -> discord.Reaction:
    if remove_reactions_on_timeout is None:
        remove_reactions_on_timeout = remove_reactions

    content = None
    embed = None
    if isinstance(timeout_message, (list, tuple)):
        content, embed = timeout_message
    elif isinstance(timeout_message, discord.Embed):
        embed = timeout_message
    else:
        content = timeout_message

    if reactions is not None:
        for reaction in reactions:
            await message.add_reaction(reaction)

    while True:
        try:
            reaction, user = await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, _: reaction.message.id == message.id,
            )
        except asyncio.TimeoutError:
            await message.edit(content=content, embed=embed)
            if reactions is not None and remove_reactions_on_timeout is True:
                try:
                    await message.clear_reactions()
                except discord.HTTPException:
                    for emoji in reactions:
                        await message.remove_reaction(emoji, ctx.bot.user)
            return None

        if user == ctx.bot.user:
            continue

        if (
            user == ctx.message.author
            and reaction is not None
            and (reactions is None or reaction.emoji in reactions)
        ):
            break

        if reactions is not None and remove_reactions is True:
            try:
                await message.remove_reaction(reaction, user)
            except (discord.HTTPException, discord.InvalidArgument):
                pass

    if reactions is not None and remove_reactions is True:
        try:
            await message.clear_reactions()
        except discord.HTTPException:
            for reaction in reactions:
                await message.remove_reaction(ctx.bot.user, reaction)

    return reaction


def escape_markdown(text: str) -> str:
    markdown_characters = ["*", "_", "`"]
    for character in markdown_characters:
        text = text.replace(character, "\\" + character)

    return text


def get_snowflake(ctx):
    channel = ctx.channel if not isinstance(ctx, DiscordChannel) else ctx
    if isinstance(channel, discord.abc.PrivateChannel):
        return channel.id
    elif isinstance(ctx.channel, discord.abc.GuildChannel):
        return channel.guild.id


def setup(bot: commands.Bot):
    bot.add_cog(HelperCommands())
