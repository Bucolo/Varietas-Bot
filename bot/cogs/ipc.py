import discord

from discord.ext import commands, ipc


class IPC(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @ipc.server.route()
    async def get_guild_count(self, data):
        return len(self.bot.guilds)

    @ipc.server.route()
    async def get_guilds(self, data):
        ids = []
        for guild in self.bot.guilds:
            ids.append(guild)
        
        return ids


def setup(bot:commands.Bot):
    bot.add_cog(IPC(bot))
