import discord
from discord.ext import commands

from database.automod import AutoModDB


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

    @commands.group(invoke_without_context=True, hidden=True)
    async def blacklist(self, ctx):
        pass

    @blacklist.command(slash_command=True, name="add", description="add a word to the blacklist")
    @commands.has_permissions(manage_guild=True)
    async def b_add(self, ctx, word=None):
        """Add a word to the blacklist."""
        if word is None:
            return await ctx.send("Please specify a word to add to the word blacklist")

        await AutoModDB(self.bot.db).add(ctx.guild.id, str(word).strip("][,"))

        await ctx.message.add_reaction("👍")

    @blacklist.command(slash_command=True, name="remove", description="remove a word from the blacklist")
    @commands.has_permissions(manage_guild=True)
    async def b_rem(self, ctx, word=None):
        """Remove a word from the blacklist"""
        if word is None:
            return await ctx.send("Please specify a word to add to the word blacklist")

        await AutoModDB(self.bot.db).remove(ctx.guild.id, str(word).strip("][,"))

        await ctx.message.add_reaction("👍")

    @blacklist.command(slash_command=True, name="get", aliases=["show"], description="get all words from your word blacklist")
    @commands.has_permissions(manage_guild=True)
    async def b_get(self, ctx):
        """Get all words from a word blacklist"""
        x = await AutoModDB(self.bot.db).get(ctx.guild.id)

        await ctx.send(f"`{str([y['word'] for y in x]).strip('][')}`")


def setup(bot: commands.Bot):
    bot.add_cog(AutoMod(bot))
