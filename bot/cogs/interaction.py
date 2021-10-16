import discord
from discord.ext import commands
import chat_exporter

import string
import ast
import random
import io

from database.ticket import TicketDB
from tools.embedbuilder import EmbedBuilder
from tools import components

class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            ctype = interaction.data["component_type"]
        except KeyError:
            return
        if ctype == 1: #Action Row
            print("received action row")
        elif ctype == 2: #Button
            if interaction.data["custom_id"] == "OpenTicket":
                member = interaction.guild.get_member(interaction.user.id)
                results = await TicketDB(self.bot.db).get(interaction.message.id)
                category = results[0]["category"]
                roles = results[0]["roles"]
                roles = ast.literal_eval(roles)
                letters = string.ascii_letters + string.digits
                code = ''.join(random.choice(letters) for i in range(5))
                category = self.bot.get_channel(int(category))
                overwrites = {
                    member: discord.PermissionOverwrite(send_messages=True, read_messages=True),
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
                print(roles)
                for role in roles:
                    role_add = interaction.guild.get_role(int(role))
                    if role_add is None:
                        role_add = interaction.guild.get_member(int(role))
                    overwrites[role_add] = discord.PermissionOverwrite(send_messages=True, read_messages=True)
                print(overwrites)
                channel = await category.create_text_channel(f"ticket-{code}", overwrites=overwrites)
                embed = EmbedBuilder(self.bot).build_embed(
                    title="Ticket opened",
                    description=f"{member.mention}, a staff member will be with you shortly\nWhen you'd like to close this ticket, press the "
                                "`❌ Close ticket` button!")
                view = components.CloseTicket()
                await channel.send(embed=embed, view=view)
                embed = EmbedBuilder(self.bot).build_embed(
                    title="Ticket Created",
                    description=f"**Ticket:** `{code}`\n**User:** {member.mention}\n**Opened at:** {self.bot.parsedate()}")
                try:
                    logchan = self.bot.get_channel(((await TicketDB(self.bot.db).get_log_channel(interaction.guild.id)))[0]["ticket_logs"])
                    await logchan.send(embed=embed)
                except:
                    pass
                await TicketDB(self.bot.db).add_ticket(interaction.guild.id, channel.id, interaction.user.id)
                
            elif interaction.data["custom_id"] == "CloseTicket":
                channel, channel_name, channel_id = interaction.channel, interaction.channel.name, interaction.channel.id
                ticket_id = channel_name[7:]
                print(await TicketDB(self.bot.db).get_member(channel_id))
                user = interaction.guild.get_member((await TicketDB(self.bot.db).get_member(channel_id))[0]["member"])
                print(user)
                transcript = await chat_exporter.export(channel)
                await channel.delete()
                embed = EmbedBuilder(self.bot).build_embed(
                    title="Ticket Closed",
                    description=f"**Ticket**: `{ticket_id}`\n**User:**{user.mention}\n**Closed at:** {self.bot.parsedate()}",
                    colour=discord.Colour.red())
                logchan = self.bot.get_channel(((await TicketDB(self.bot.db).get_log_channel(interaction.guild.id)))[0]["ticket_logs"])
                if transcript is None:
                    transcript_file=None
                else:
                    transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{ticket_id}.html")
                try:
                    await logchan.send(embed=embed)
                    await logchan.send(file=transcript_file)
                except:
                    pass
                
        elif ctype == 3: #Select Menu
            print("received select menu")
    
def setup(bot):
    bot.add_cog(Interactions(bot))