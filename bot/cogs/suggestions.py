import discord
from discord.ext import commands

from database.suggestions import SuggestDB


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="suggest", slash_command=True, invoke_without_command=True)
    async def suggest(self, ctx):
        pass
    
    @suggest.command(slash_command=True)
    async def send(self, ctx, *, suggestion=None):
        """Send a suggestion to your server's suggestion channel"""
        if suggestion is None:
            return await ctx.send("Please specify a suggestion")

        con = SuggestDB(self.bot.db)
        channel = await con.get(ctx.guild.id)
        try:
            channel = await self.bot.fetch_channel(channel[0].get("channel"))
        except:
            return await ctx.send("Could not find a suggestions channel for this server in my database. Please ask a server admin to reconfigure or update the suggestions channel for your server.")
        
        embed = discord.Embed(
            title=f"New Suggestion from `{ctx.author.name}#{ctx.author.discriminator}`",
            description=suggestion,
            colour=0x66bb6a
        )
        msg = await channel.send(embed=embed)
        
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        await ctx.send("Sent! Thanks for your suggestion.")
    
    @suggest.command(slash_command=True)
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx):
        """Remove your suggestion channel from the bot's database."""
        await SuggestDB(self.bot.db).delete(ctx.guild.id)
        
        await ctx.send("Done!")
    
    @suggest.command(slash_command=True)
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, channel: discord.TextChannel=None):
        """Set your suggestion channel to a given channel where you want all suggestions to be sent to."""
        if channel is None:
            return await ctx.send("Please ping a channel where you want all suggestions to be sent")
        
        try:
            await SuggestDB(self.bot.db).set(channel, ctx.guild.id)
        except commands.CommandInvokeError:
            return await ctx.send(f"You already have a suggestion channel set! to change it, update it with {ctx.prefix}suggestion update <channel>.")

        await ctx.send("Done!")
    
    @suggest.command(slash_command=True)
    @commands.has_permissions(manage_guild=True)
    async def update(self, ctx, channel: discord.TextChannel = None):
        """Update your suggestion channel to a given channel where you want all suggestions to be sent to."""
        if channel is None:
            return await ctx.send("Please specify a channel where you want all suggestions to be sent.")
        
        try:
            await SuggestDB(self.bot.db).update(channel, ctx.guild.id)
        except commands.CommandInvokeError as e:
            return await ctx.send(f"You don't have a suggestion channel setup! To set it, use {ctx.prefix}suggest set <channel>.")
        
        await ctx.send("Done!")

    
def setup(bot):
    bot.add_cog(Suggestions(bot))