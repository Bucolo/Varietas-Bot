import discord

from discord.ext import commands

from discord_components import *
from dislash import InteractionClient, ActionRow, Button, ButtonStyle, SelectMenu, SelectOption
from database import ticket

from tools import embedbuilder

import asyncio


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ic = InteractionClient(bot)
        self.e = embedbuilder.EmbedBuilder(self.bot)

    # async def cog_command_error(self, ctx, error):
    #     if isinstance(error, commands.errors.CommandInvokeError) and "Invalid Form Body" in str(error.original):
    #         embed = self.e.build_embed(
    #             title="Command Error",
    #             description="This category doesn't have any text channels available. Please re-use the command",
    #             timestamp=True
    #         )
    #         await ctx.send(embed=embed, delete_after=20.0)

    #     elif isinstance(error, commands.CommandOnCooldown):
    #         embed = self.e.build_embed(
    #             title="Command Error",
    #             description=f"{error.message} seconds",
    #             timestamp=True
    #         )
    #         await ctx.send(embed=embed, delete_after=20.0)

    #     elif isinstance(error, asyncio.TimeoutError):
    #         embed = self.e.build_embed(
    #             title="Command Error",
    #             description="You ran out of time. Please re-use the command.",
    #             timestamp=True
    #         )

    #         await ctx.send(embed=embed, delete_after=20.0)

    #     else:
    # return await ctx.send(f"Unknown Error (Please report this using
    # `v!feedback`):\n{error}")

    @commands.group(name="ticket", invoke_without_command=True)
    async def ticket(self, ctx):
        pass

    @ticket.command(
        name="setup",
        aliases=[],
        description="Setup a ticket system in your server"
    )
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def ticket_setup(self, ctx):
        title = ""
        desc = ""
        chan_id = 0
        roles = []
        cat_id = 0

        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please enter the title for the ticket embed",
        )

        def check(m):
            return m.author.id != self.bot.user.id and m.author.id == ctx.author.id

        embed1 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        title = msg.content
        await embed1.delete()
        await msg.delete()

        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please enter the description for the ticket embed"
        )
        embed2 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        desc = msg.content
        await msg.delete()
        await embed2.delete()

        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Category where the channel you would like the ticket embed to be sent is in.")

        msg = await ctx.send(
            embed=embed,
            components=[
                SelectMenu(
                    custom_id="_cat_id",
                    placeholder="Category where the channel you want the embed to be sent is in",
                    options=[
                        SelectOption(l.name, l.id) for l in ctx.guild.categories
                    ]
                )
            ]
        )

        def _check(inter):
            return inter.author == ctx.author

        inter = await msg.wait_for_dropdown(_check)

        cat_id = [option.value for option in inter.select_menu.selected_options]

        await msg.delete()

        category = self.bot.get_channel(int(cat_id[0]))

        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please select the channel where you want the embed to be sent in.")

        msg = await ctx.send(
            embed=embed,
            components=[
                SelectMenu(
                    custom_id="chan_id",
                    placeholder="channel where you want the embed to be sent in",
                    options=[
                        SelectOption(l.name, l.id) for l in category.text_channels
                    ]
                )
            ]
        )

        inter = await msg.wait_for_dropdown(_check)

        chan_id = [
            option.value for option in inter.select_menu.selected_options]

        await msg.delete()

        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please ping the roles that will automatically have access to ticket channels")
        embed4 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        roles_str = msg.content.strip("<@&>")
        roles = str(msg.content.strip('<@&').split('>'))
        await embed4.delete()
        await msg.delete()

        embed = self.e.build_embed(
            title="Please confirm your options:",
            description=f"Title: {title}\nDescription: {desc}\nChannel: {self.bot.get_channel(int(chan_id[0])).mention}\nTicket Category: {self.bot.get_channel(int(cat_id[0])).name}\nRoles: {roles_str}"
        )

        msg = await ctx.send(embed=embed, components=[Button(style=ButtonStyle.green, label="✅"),
                                                      Button(style=ButtonStyle.red, label="❌")])

        def check(c): return c.author == ctx.author and c.channel == ctx.channel
        try:
            interaction = await self.bot.wait_for("button_click", check=check)
            if interaction.component.label == "✅":
                e = self.e.build_embed(
                    title=title,
                    description=desc,
                    timestamp=True)
                channel = self.bot.get_channel(int(chan_id[0]))
                msg = await channel.send(embed=e)
                t = ticket.TicketDB(self.bot.db)
                await t.add(int(cat_id[0]), msg.id, roles)

                await msg.add_reaction("📥")
                await interaction.respond(content=f"Your ticket has been created in {channel.mention}!")
            elif interaction.component.label == "❌":
                await interaction.respond(content="No problem. Re-use the command and enter your desired answers.")
            else:
                pass
            return
        except asyncio.TimeoutError:
            return


def setup(bot):
    bot.add_cog(Tickets(bot))
