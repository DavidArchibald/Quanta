#!/usr/bin/env python3

import discord
from discord.ext import commands

from string import ascii_lowercase, ascii_uppercase


class CodeCommands:
    """Commands for codes and Ciphers."""

    icon = "<:quantacode:473976436051673091>"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="Rotate",
        usage="rotate [degree]",
        aliases=["rot", "caesar_cipher", "caesar-cipher", "caesarcipher", "caesar"],
    )
    async def rotate(self, ctx: commands.Context, degree="", *, message: str = ""):
        """Implements a rotate cipher. Using caesarcipher sets it to a degree of 13.

        Arguments:
            ctx {commands.Context} -- Information about where the command was run.

        Keyword Arguments:
            degree {int} -- How many character to rotate the alphabet. (default: {""})
            message {str} -- The message to rotate. (default: {""})
        """

        if ctx.invoked_with.startswith("caesar"):
            message = f"{degree} {message}"
            degree = 13
        elif degree is None or degree == "" or message is None or message == "":
            await ctx.send("I need a degree and message to use for the cipher.")
        elif isinstance(degree, str):
            degree_signs = ("°", "deg", "degree", "degrees")
            for degree_sign in degree_signs:
                if degree.endswith(degree_sign):
                    degree = degree[: len(degree_sign)]
                    break
                elif message.startswith(degree_sign):
                    message = message[len(degree_sign) :]
                    break
            try:
                degree = int(degree)
            except ValueError:
                await ctx.send("I need a valid, integer degree to use for the cipher.")
                return

        original_degree = degree
        if degree > 26:
            degree = degree % 26

        shift = str.maketrans(
            ascii_lowercase + ascii_uppercase,  # Normal Alphabet
            ascii_lowercase[degree:]  # Rotated Lowercase
            + ascii_lowercase[:degree]
            + ascii_uppercase[degree:]  # Rotated Uppercase
            + ascii_uppercase[:degree],
        )
        rotated_message = message.translate(shift)

        embed = discord.Embed(
            title="Caesar Cipher"
            if ctx.invoked_with.startswith("caesar")
            else f"Rot{original_degree} Cipher",
            description=f"**{rotated_message}**",
            colour=0x00FF00,
        )
        embed.set_footer(text=f"Original Message: {message}")

        await ctx.send(embed=embed)

    def get_embed(self, message, cipher, cipher_name=""):
        embed = discord.Embed(
            title=f"{cipher_name} Cipher", description=f"**{cipher}**", colour=0x00FF00
        )
        embed.set_footer(text=f"Original Message: {message}")
        return embed


def setup(bot: commands.Bot):
    bot.add_cog(CodeCommands(bot))
