import discord
from discord.ext import commands

from tools import embedbuilder as e, components
from psutil import Process, cpu_percent
from os import getpid
import json
from database.prefix import PrefixDB
from database.event import EventDB
from database.cases import CasesDB

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                {error.original}
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                retry after: {error.retry_after} seconds
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                {error.message}
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)

    @commands.command(slash_command=True, description="displays bot information")
    async def info(self, ctx):
        """Send bot information."""
        msg = f"""**Bot version:** `{self.bot.__version__}`
**Database Version:** `{self.bot.db.__version__}`
**Edpy version:** `{discord.__version__}`
**Guild Count:** `{len(self.bot.guilds)}`
**Memory Used:** `{round(Process(getpid()).memory_info().rss/1204/1204/1204, 3)}GB Used ({round(Process(getpid()).memory_percent())}%)`
**CPU Usage:** `{cpu_percent()}%`
**Creators:** `Andeh#2709`, `Erase#0027`
"""

        embed = e.EmbedBuilder(self.bot).build_embed(
            title="Bot information",
            description=msg,
            thumb=str(self.bot.user.avatar),
            timestamp=True
        )

        await ctx.send(embed=embed)

    @commands.command(slash_command=True, description="change the bot's prefix")
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, new_prefix=None):
        """Change the bot's prefix"""
        if new_prefix is None:
            embed = e.EmbedBuilder(
                self.bot).build_embed(
                title=f"The prefix for `{ctx.guild.name}` is `{ctx.prefix}`", 
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

    @commands.command(slash_command=True, description="send feedback to the developer server")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def feedback(self, ctx, *, message=None):
        """Send feedback to the developer server"""
        if message is None:
            return await ctx.send("Please specify a message!")
        
        channel = await self.bot.fetch_channel(888491767505227786)
        
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Feedback from {ctx.author.name}#{ctx.author.discriminator}",
            description=message,
            timestamp=True
        )
        
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        await ctx.send("Message sent! Thanks for your feedback!")
        
    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        return
    
    @config.command()
    @commands.has_permissions(manage_guild=True)
    async def muted(self, ctx, role: discord.Role):
        """Setup muted role for your guild."""
        await CasesDB(self.bot.db).add_muted_role(ctx.guild.id, role.id)
        await ctx.send("Added muted role to db")
    
    @commands.group(slash_command=True, invoke_without_command=True)
    async def logs(self, ctx):
        pass
    
    @logs.command(slash_command=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def setup(self, ctx):
        """Setup log configuration."""
        view=components.LogsBase.DropdownView()
        embed = e.EmbedBuilder(self.bot).build_embed(
            title="Logs configuration",
            description="See the dropdown below to edit the channels for where you want to have logs sent!\n\nSelect **ALL** to have all logs sent to one channel.\n"
                        "Or have each log type sent to different channels by selecting them individually.\n"
                        "Or we can set them all up for you automatically!")
        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Config(bot))
