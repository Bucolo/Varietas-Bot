import discord

from discord.ext import commands

from database import ticket

from tools import embedbuilder, components

import asyncio


class Tickets2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e = embedbuilder.EmbedBuilder(self.bot)

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

    @commands.group(name="ticket", invoke_without_command=True, description="ticket functionalities")
    @commands.has_permissions(manage_guild=True)
    async def ticket(self, ctx):
        pass

    @ticket.command(slash_command=True, 
        name="setup",
        aliases=[],
        description="Setup a ticket system in your server"
    )
    @commands.cooldown(1, 30, commands.BucketType.member)
    @commands.has_permissions(manage_guild=True)
    async def ticket_setup(self, ctx):
        """Setup a ticket system in your server"""
        title = ""
        desc = ""
        chan_id = 0
        roles = []
        cat_id = 0

#TICKET TITLE
        embed = self.e.build_embed(title="Ticket System Setup", description="Please enter the title for the ticket embed")
        check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        embed1 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        title = msg.content
        await embed1.delete()
        await msg.delete()

#TICKET DESCRIPTION
        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please enter the description for the ticket embed"
        )
        embed2 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        desc = msg.content
        await msg.delete()
        await embed2.delete()

#TICKET PANEL CATEGORY
        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Category where the channel you would like the ticket panel to be sent is in.") 
        view = components.TicketSetupPanelCat.DropdownView(ctx)
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        cat_id = view.values[0]
        await msg.delete()
        category = self.bot.get_channel(int(cat_id))

#TICKET PANEL CHANNEL
        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please select the channel where you want the panel to be sent in.")
        view = components.TicketSetupPanelChan.DropdownView(category)
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        chan_id = view.values[0]
        await msg.delete()
        
#TICKET CATEGORY
        embed = self.e.build_embed(
            title="Ticket System Setup", description="Please select the category where we should create the tickets.")
        view = components.TicketCategory.DropdownView(ctx)
        msg = await ctx.channel.send(embed=embed, view=view)
        await view.wait()
        category_id = view.values[0]
        await msg.delete()
        
#TICKET ROLES AND MEMBERS
        embed = self.e.build_embed(
            title="Ticket System Setup",
            description="Please ping the roles and/or members that will automatically have access to ticket channels")
        embed4 = await ctx.channel.send(embed=embed)
        msg = await self.bot.wait_for('message', timeout=180.0, check=check)
        roles = msg.raw_role_mentions
        members = msg.raw_mentions
        roles_str = []
        for role in roles:
            if type(role) == int: 
                role = ctx.guild.get_role(role)
            roles_str.append(role.mention)
        for member in members:
            if type(member) == int:
                member = ctx.guild.get_member(member)
            roles_str.append(member.mention)
        for member in msg.raw_mentions:
            roles.append(member)
        roles_str = str(roles_str).replace("[", "").replace("]", "").replace("'", "")
        await embed4.delete()
        await msg.delete()

#TICKET LOGS CATEGORY  
        logchan = await ticket.TicketDB(self.bot.db).get_log_channel(ctx.guild.id)
        print(logchan)
        if logchan is None or logchan == []:
            view = components.TicketSetupLogCat.DropdownView(ctx)
            embed = self.e.build_embed(
                title="Select log category",
                description="You don't seem to have a ticket log channel set up.\nPlease select the category of the channel where you want me to send ticket logs and transcripts!")
            msg = await ctx.channel.send(embed=embed, view=view)
            await view.wait()
            log_cat_id = view.values[0]
            log_cat = ctx.guild.get_channel(int(log_cat_id))
            await msg.delete()

#TICKET LOGS CHANNEL        
            view = components.TicketSetupLogChan.DropdownView(log_cat)
            embed = self.e.build_embed(
                title="Select log channel",
                description="Please select the channel where you want me to send ticket logs and transcripts!")
            msg = await ctx.channel.send(embed=embed, view=view)
            await view.wait()
            log_chan_id = view.values[0]
            await msg.delete()
        else:
            log_chan_id = logchan[0]["ticket_logs"]

#FINAL CONFIRMATION
        logchan = self.bot.get_channel(int(log_chan_id))
        embed = self.e.build_embed(
            title="Please confirm your options:",
            description=f"Title: {title}\nDescription: {desc}\nChannel: {self.bot.get_channel(int(chan_id)).mention}\nTicket Category: {self.bot.get_channel(int(cat_id)).name}\nRoles: {roles_str}\nTicket Log Channel: {logchan.mention}")
        view=components.TicketSetupConfirm()
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.value:
            e = self.e.build_embed(
                title=title,
                description=desc,
                timestamp=True)
            channel = self.bot.get_channel(int(chan_id))
            view = components.OpenTicket()
            await msg.delete()
            msg = await channel.send(embed=e, view=view)
            await ctx.message.delete()

#ADDING TO THE DATABASE
            roles = str(roles)
            t = ticket.TicketDB(self.bot.db)
            await t.add(int(ctx.guild.id), int(category_id), int(msg.id), str(roles))
            await t.add_log_channel(int(log_chan_id), ctx.guild.id)
            embed = self.e.build_embed(
                title="Your ticket panel has been created!",
                description=f"Title: {title}\nDescription: {desc}\nChannel: {self.bot.get_channel(int(chan_id)).mention}\nTicket Category: {self.bot.get_channel(int(cat_id)).name}\nRoles: {roles_str}\nTicket Log Channel: {logchan.mention}")
            await ctx.send(embed=embed)
            return
        else:
            embed = self.e.build_embed(
                title="Ticket panel setup cancelled",
                description=f"To create another, simply run `{ctx.prefix}ticket setup` again.\nTo change the ticket log channel, run `{ctx.prefix}config logs`.")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tickets2(bot))