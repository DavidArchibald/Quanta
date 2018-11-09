import asyncio
import discord

from typing import List, Optional, Tuple, Union

from ..helpers.helper_functions import get_snowflake
from ..globals.custom_types import DiscordReaction

# from ..globals.variables import database

games = []


class Game:
    def __init__(self, ctx):
        self._message: discord.Message = None
        self.ctx = ctx

        self._snowflake = get_snowflake(ctx)

    async def modify_game(self, content=None, embed=None):
        if self._message is None:
            self._message = await self.ctx.send(content=content, embed=embed)
        else:
            await self._message.edit(content=content, embed=embed)

    async def wait_for_reactions(
        self,
        message: discord.Message = None,
        reactions: Optional[Union[List[DiscordReaction], Tuple]] = None,
        timeout: Union[int, float] = 60.0,
        timeout_message: Union[
            str, discord.Embed, Tuple[str, discord.Embed], List
        ] = "Timed out!",
        remove_reactions: bool = True,
        remove_reactions_on_timeout: bool = None,
    ) -> discord.Reaction:
        remove_reactions_on_timeout = (
            remove_reactions
            if remove_reactions_on_timeout is None
            else remove_reactions_on_timeout
        )

        message = self.message if message is None else message

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
                reaction, user = await self.ctx.bot.wait_for(
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
                            await message.remove_reaction(emoji, self.ctx.bot.user)
                return None

            if user == self.ctx.bot.user:
                continue

            if (
                user == self.ctx.message.author
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
                    await message.remove_reaction(self.ctx.bot.user, reaction)

        return reaction


def get_game(ctx):
    global games

    snowflake = get_snowflake(ctx)
    try:
        return next(game for game in games if game._channel_snowflake == snowflake)
    except StopIteration as exception:
        game = Game(ctx)
        games.append(game)
        return game
