import discord
from discord.ext import commands

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def reminder(self, ctx, duration, *, reminder):
        return
    
def setup(bot):
    bot.add_cog(Reminders(bot))