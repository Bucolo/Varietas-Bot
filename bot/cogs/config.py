import discord
from discord.ext import commands

from tools import embedbuilder as e
from psutil import Process, cpu_percent
from os import getpid
import json
from database.prefix import PrefixDB


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        msg = f"""**Bot version:** `{self.bot.__version__}`
**Database Version:** `{self.bot.db.__version__}`
**Enhanced-Dpy version:** `{discord.__version__}`
**Server Count:** `{len(self.bot.guilds)}`
**Memory Used:** `{round(Process(getpid()).memory_info().rss/1204/1204/1204, 3)}GB Used ({round(Process(getpid()).memory_percent())}%)`
**CPU Usage:** `{cpu_percent()}%`
**Creators:** `Andeh#2709`, `Erase#0027`
"""

        embed = e.EmbedBuilder(self.bot).build_embed(
            title="Bot information",
            description=msg,
            thumb=self.bot.user.avatar_url_as(static_format="png"),
            timestamp=True
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, new_prefix=None):
        if new_prefix is None:
            embed = e.EmbedBuilder(
                self.bot).build_embed(
                title=f"The prefix for `{ctx.guild.name}` is `{prefix}`", 
                timestamp=True
            )
            return await ctx.message.reply(embed=embed)
        
        con = PrefixDB(self.bot.db)
        await con.update(ctx.guild.id, new_prefix)
        
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Prefix for `{ctx.guild.name}` set to `{new_prefix}`",
            timestamp=True
        )
        
        return await ctx.message.reply(embed=embed)
    
        
        


def setup(bot):
    bot.add_cog(Config(bot))
