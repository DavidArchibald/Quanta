import discord
from discord.ext import commands

class GetUserConverter(commands.Converter):
    async def convert(self, ctx, username):
        user = username
        print(username)
        if username == None:
            print('None')
        try:
            user = await commands.UserConverter().convert(ctx, username)
        except Exception as e:
            pass
        return user
