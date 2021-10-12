import discord
from discord.ext import commands

from tools.embedbuilder import EmbedBuilder

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e = EmbedBuilder(self.bot)
    
#MESSAGE LOGS
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        return
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, message):
        return
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        return
    
#SERVER LOGS
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        return
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        return
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        return
    
    @commands.Cog.listener()
    async def on_integration_create(self, integration):
        return