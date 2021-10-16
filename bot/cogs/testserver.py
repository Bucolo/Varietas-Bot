import discord
from discord.ext import commands
import asyncio
from dislash import InteractionClient, ActionRow, Button, ButtonStyle, SelectMenu, SelectOption

from tools.customchecks import *

class TestServer(commands.Cog):
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

    @commands.Cog.listener()
    @Check.devserver()
    async def on_member_join(self, member):
        role = discord.utils.find(lambda r: r.id == 887769244241125416)
        await member.add_roles(role)

    @commands.command(slash_command=True, aliases=['ms'], hidden=True)
    @Check.botadmin()
    async def makestaff(self, ctx, member: discord.Member):
        await member.add_roles(ctx.guild.get_role(887770743323131964))
        embed = discord.Embed(
            description=f"Successfully made `{member}` a developer. Remember to add them to the GitHub group!")
        row = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Go to GitHub",
                url="https://github.com/orgs/VarietasDev/"))
        await ctx.send(embed=embed, components=[row])

    @commands.command(slash_command=True, aliases=['mh'], hidden=True)
    @Check.botadmin()
    async def makehelper(self, ctx, member: discord.Member):
        await member.add_roles(ctx.guild.get_role(887814647510609950))
        embed = discord.Embed(
            description=f"Successfully made `{member}` a helper. Remember to add them to the GitHub group!")
        row = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Go to GitHub",
                url="https://github.com/orgs/VarietasDev/"))
        await ctx.send(embed=embed, components=[row])

    @commands.command(slash_command=True, description="add a bot to the developer server")
    @Check.devserver()
    async def addbot(self, ctx, bot_id, *, reason=None):
        """Add a bot to the developer server"""
        row = ActionRow(Button(style=ButtonStyle.link, label="Go to Developer Portal", url="https://discord.com/developers/applications"))
        try:
            int(bot_id)
        except ValueError:
            embed = discord.Embed(description="Please provide the id of your bot.", colour=discord.Colour.red())
            await ctx.message.reply(embed=embed, components=[row])
            return
        if reason is None:
            embed = discord.Embed(description="Please provide a reason for us to add your bot. If you have already discussed it with one of the <@&887771119661244447>"
                                              "then simply put 'Already discussed' or similar.", colour=discord.Colour.red())
            await ctx.message.reply(embed=embed)
            return
        channel = self.bot.get_channel(887824793234202654)
        bot_invite = f"https://discord.com/api/oauth2/authorize?client_id={str(bot_id)}&permissions=517614194241&scope=bot%20applications.commands"
        embed = discord.Embed(
            title=f"Bot invite request from {ctx.author}",
            description=f"**User:** {ctx.author.mention}\n**Reason:** {reason}\n**[Invite]({bot_invite})**\n\n**Submitted at:** {self.bot.parsedate()}",
            colour=discord.Colour.green())
        await channel.send("<@&887771119661244447>")
        await channel.send(embed=embed)
        embed = discord.Embed(
            title="Success!",
            description=f"**{ctx.author.name}**, Your bot has been published to the <@&887771119661244447>! Please allow them time to review your request and invite your bot.",
            colour=discord.Colour.green())
        await ctx.message.reply(embed=embed)
        await ctx.message.delete()

    @commands.Cog.listener()
    @Check.devserver()
    async def on_member_update(self, before, after):
        if (before.guild.id == 872313085455650846) and (before.pending and not after.pending):
            await after.add_roles(after.guild.get_role(887769244241125416))
            embed = discord.Embed(
                title=f"Welcome to the server, {after.name}",
                description=f"{after.mention}, make sure to look over our <#887832966649241631> and <#887833852670791690> channels to get a better idea on what the server is about!",
                colour=discord.Colour.green())
            embed.set_thumbnail(url=str(after.avatar))
            await self.bot.get_channel(887830918344114176).send(embed=embed)

def setup(bot):
    bot.add_cog(TestServer(bot))
