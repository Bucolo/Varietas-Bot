import discord
from discord.ext import commands

from database.automod import AutoModDB


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_context=True)
    async def blacklist(self, ctx):
        #Just here to create the group
        pass

    @blacklist.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def b_add(self, ctx, word=None):
        if word is None:
            return await ctx.send("Please specify a word to add to the word blacklist")

        await AutoModDB(self.bot.db).add(ctx.guild.id, str(word).strip("][,"))

        await ctx.message.add_reaction("👍")

    @blacklist.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def b_rem(self, ctx, word=None):
        if word is None:
            return await ctx.send("Please specify a word to add to the word blacklist")

        await AutoModDB(self.bot.db).remove(ctx.guild.id, str(word).strip("][,"))

        await ctx.message.add_reaction("👍")

    @blacklist.command(name="get", aliases=["show"])
    @commands.has_permissions(manage_guild=True)
    async def b_get(self, ctx):
        x = await AutoModDB(self.bot.db).get(ctx.guild.id)

        await ctx.send(f"`{str([y['word'] for y in x]).strip('][')}`")


def setup(bot: commands.Bot):
    bot.add_cog(AutoMod(bot))
