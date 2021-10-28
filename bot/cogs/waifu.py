import discord
from discord.ext import commands

import asyncio
import random
from waifuim import WaifuAioClient

class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(invoke_without_command=True)
    async def waifu(self, ctx):
        """Displays a SFW Waifu"""
        if ctx.guild.id == 420959440015982592:
            return
        waifu_url = await self.bot.wf.sfw('waifu')
        embed = discord.Embed(title="A waifu has appeared", colour=discord.Colour.purple())
        embed.set_image(url=waifu_url)
        await ctx.message.reply(embed=embed)
        
    @waifu.command()
    async def nsfw(self, ctx):
        """Displays a NSFW Waifu"""
        if ctx.guild.id == 420959440015982592:
            return
        if ctx.channel.nsfw:
            waifu_url = await self.bot.wf.nsfw('ero', gif=False)
            embed = discord.Embed(title="A waifu has appeared", colour=discord.Colour.purple())
            embed.set_image(url=waifu_url)
            return await ctx.message.reply(embed=embed)
        await ctx.send(embed=discord.Embed(title="This command only works in nsfw channels!", colour=discord.Colour.red()))
            
def setup(bot):
    bot.add_cog(Waifu(bot))