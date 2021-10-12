import discord
from . import helpembeds as he
from .embedbuilder import EmbedBuilder
from database.ticket import TicketDB
import string
import ast
import random
from urllib.parse import quote_plus

class HelpBase:

    class Dropdown(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Main Menu", value="Main Menu"),
                discord.SelectOption(label="News", value="News"),
                discord.SelectOption(label="Moderation", value="Moderation"),
                discord.SelectOption(label="Miscellaneous", value="Miscellaneous"),
                discord.SelectOption(label="Utility", value="Utility"),
                discord.SelectOption(label="Music", value="Music"),
                discord.SelectOption(label="Fun", value="Fun"),
                discord.SelectOption(label="Economy", value="Economy"),
                discord.SelectOption(label="Configuration", value="Configuration")
            ]
            super().__init__(placeholder="What command category would you like to view?", options=options)

        async def callback(self, interaction: discord.Interaction):
            if interaction.data["values"] == ["Main Menu"]:
                await interaction.message.edit(embed=he.HelpEmbeds.mainmenu())
            if interaction.data["values"] == ["News"]:
                await interaction.message.edit(embed=he.HelpEmbeds.news())
            if interaction.data["values"] == ["Moderation"]:
                await interaction.message.edit(embed=he.HelpEmbeds.moderation())
            if interaction.data["values"] == ["Miscellaneous"]:
                await interaction.message.edit(embed=he.HelpEmbeds.miscellaneous())
            if interaction.data["values"] == ["Utility"]:
                await interaction.message.edit(embed=he.HelpEmbeds.utility())
            if interaction.data["values"] == ["Music"]:
                await interaction.message.edit(embed=he.HelpEmbeds.music())
            if interaction.data["values"] == ["Fun"]:
                await interaction.message.edit(embed=he.HelpEmbeds.fun())
            if interaction.data["values"] == ["Economy"]:
                await interaction.message.edit(embed=he.HelpEmbeds.economy())
            if interaction.data["values"] == ["Configuration"]:
                await interaction.message.edit(embed=he.HelpEmbeds.configuration())
        
    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(HelpBase.Dropdown())
            
class TicketSetupPanelCat:
    
    class Dropdown(discord.ui.Select):
        def __init__(self, ctx):
            self.ctx = ctx
            options = [discord.SelectOption(label=l.name, value=str(l.id)) for l in self.ctx.guild.categories]
            super().__init__(placeholder="Category where the channel you want the panel to be sent is in", options=options, min_values=1, max_values=1)
            
        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
            
    
    class DropdownView(discord.ui.View):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__()
            self.add_item(TicketSetupPanelCat.Dropdown(self.ctx))
            
class TicketSetupPanelChan:
    
    class Dropdown(discord.ui.Select):
        def __init__(self, cat):
            self.cat = cat
            options = [discord.SelectOption(label=l.name, value=str(l.id)) for l in self.cat.text_channels]
            super().__init__(placeholder="Select the channel where you want the ticket panel to send", options=options, min_values=1, max_values=1)
            
        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
            
    class DropdownView(discord.ui.View):
        def __init__(self, cat):
            self.cat = cat
            super().__init__()
            self.add_item(TicketSetupPanelChan.Dropdown(self.cat))
            
class TicketCategory:
    
    class Dropdown(discord.ui.Select):
        def __init__(self, ctx):
            self.ctx = ctx
            options = [discord.SelectOption(label=l.name, value=str(l.id)) for l in self.ctx.guild.categories]
            super().__init__(placeholder="Category where the channel you want the tickets to be created in", options=options, min_values=1, max_values=1)
            
        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
            
    class DropdownView(discord.ui.View):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__()
            self.add_item(TicketCategory.Dropdown(self.ctx))
            
class TicketSetupLogCat:
    
    class Dropdown(discord.ui.Select):
        def __init__(self, ctx):
            self.ctx = ctx
            options = [discord.SelectOption(label=l.name, value=str(l.id)) for l in self.ctx.guild.categories]
            super().__init__(placeholder="Category where the channel you want the logs to be sent is in", options=options, min_values=1, max_values=1)
            
        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
            
    
    class DropdownView(discord.ui.View):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__()
            self.add_item(TicketSetupLogCat.Dropdown(self.ctx))
            
class TicketSetupLogChan:
    
    class Dropdown(discord.ui.Select):
        def __init__(self, cat):
            self.cat = cat
            options = [discord.SelectOption(label=l.name, value=str(l.id)) for l in self.cat.text_channels]
            super().__init__(placeholder="Select the channel where you want the ticket embed to send", options=options, min_values=1, max_values=1)
            
        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
            
    class DropdownView(discord.ui.View):
        def __init__(self, cat):
            self.cat = cat
            super().__init__()
            self.add_item(TicketSetupLogChan.Dropdown(self.cat))
            
class TicketSetupConfirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        
    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Sending Ticket...", ephemeral=True)
        self.value = True
        self.stop()
        
    @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelling ticket panel setup...", ephemeral=True)
        self.value = False
        self.stop()
        
class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="❌", custom_id="CloseTicket")
    async def closeticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        return

class OpenTicket(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="📥", custom_id="OpenTicket")
    async def openticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        return
    
class LogsBase:
    
    class Dropdown(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="All", value="All"),
                discord.SelectOption(label="Create channels for me", value="Create"),
                discord.SelectOption(label="Channel Logs", value="ChannelLogs"),
                discord.SelectOption(label="Server Logs", value="ServerLogs"),
                discord.SelectOption(label="Member Logs", value="MemberLogs"),
                discord.SelectOption(label="Message Logs", value="MessageLogs"),
                discord.SelectOption(label="Voice Logs", value="VoiceLogs"),
                discord.SelectOption(label="Ticket Logs", value="TicketLogs")
            ]
            super().__init__(placeholder="What log channel would you like to configure?", options=options)

        async def callback(self, interaction: discord.Interaction):
            self.view.values = self.values
            self.view.stop()
        
    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(LogsBase.Dropdown())
            
class Avatar(discord.ui.View):
    def __init__(self, link: str, member: discord.Member):
        super().__init__()
        self.add_item(discord.ui.Button(label=f"{member}'s avatar", url=link))