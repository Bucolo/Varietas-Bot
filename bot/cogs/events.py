from database.cases import CasesDB
import discord
from discord.ext import commands
import string
import random
import json
import ast

from database.ticket import TicketDB
from tools.embedbuilder import EmbedBuilder
from tools.customchecks import Check
from database.automod import AutoModDB
from database.prefix import PrefixDB
from database.event import EventDB
import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e = EmbedBuilder(self.bot)
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
    async def on_message(self, message):
        return
        if message.guild and not message.author.bot:
            x = await AutoModDB(self.bot.db).get(message.guild.id)

            msg = discord.utils.escape_markdown(message.content)

            for y in x:
                if y["word"] in msg and message.author.id != self.bot.user.id:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} That isn't allowed here!")

            if (message.channel.id == 887815737052377128) and (message.embeds):
                if message.author.id == 883464643304116255:
                    return
                for embed in message.embeds:
                    embed.colour = discord.Colour.green()
                    await message.channel.send(embed=embed)
                    await message.delete()
                    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        con = PrefixDB(self.bot.db)
        
        await con.add(guild.id, "v!")
        
        con = EventDB(self.bot.db)
        
        await con.add(guild=guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        con = PrefixDB(self.bot.db)
        await con.remove(guild.id)
        
        con = EventDB(self.bot.db)
        await con.remove(guild=guild.id)
        
        con = CasesDB(self.bot.db)
        await con.delete(guild.id)
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        con = EventDB(self.bot.db)
        res = await con.get(channel.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Channel Created",
            description=f"Channel: {channel.mention}\nName: `{channel.name}`\nCategory: `{channel.category}`",
            colour=0x66bb6a
        )
        
        embed.add_field(
            name="Attributes:", 
            value=f"Created at: {discord.utils.format_dt(channel.created_at, style='f')}"
        )
        
        channel = await self.bot.fetch_channel(int(res[0].get("channel_logs")))
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        con = EventDB(self.bot.db)
        res = await con.get(channel.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Channel Deleted",
            description=f"Name: `{channel.name}`\nCategory: `{channel.category}`",
            colour=0xef534e
        )
        
        embed.add_field(
            name="Attributes:",
            value=f"Created at: {discord.utils.format_dt(channel.created_at, style='f')}"
        )
        
        channel = await self.bot.fetch_channel(int(res[0].get("channel_logs")))
        
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        con = EventDB(self.bot.db)
        res = await con.get(before.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Channel Updated",
            description=f"Channel: {after.mention}\n",
            colour=0x66bb6a
        )
        
        if before.name != after.name:
            embed.description += f"Channel Name: `{before.name}` -> `{after.name}`\n"
        
        if before.position != after.position:
            embed.description += f"Channel Position: `{before.position}` -> `{after.position}`\n"
        
        if before.overwrites != after.overwrites:
            for name in after.overwrites.items():
                if name not in before.overwrites.items():
                    embed.description += f"Permission Added -> `{name.name}`\n"
        print(res[0])
        channel = await self.bot.fetch_channel(int(res[0].get("channel_logs")))
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        con = EventDB(self.bot.db)
        res = await con.get(after.id)
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
    
        embed = discord.Embed(
            title="Server Updated",
            description="",
            colour=0x66bb6a
        )
        if before.owner != after.owner:
            embed.description += f"Server Owner: {before.owner.mention} -> {after.owner.mention}\n"
        
        if str(before.icon) != str(after.icon):
            embed.description += f"Server Icon: {str(before.icon)} -> {str(after.icon)}\n"
        
        if str(before.banner) != str(after.banner):
            embed.description += f"Server Banner: {str(before.banner)} -> {str(after.banner)}\n"
        
        _ = []
        for cat in after.categories:
            _.append(cat.mention)
        r = ", ".join(_)

        try:
            added = iter(cat for cat in after.categories if cat not in before.categories)
            catAdded = next(added)
            
            if added:
                embed.description += f"Category Created: {catAdded.mention}\nCategories: {r}\n"
        except StopIteration:
            pass
        try:
            removed = iter(cat for cat in before.categories if cat not in after.categories)
            catRemoved = next(removed)
            if removed:
                embed.description += f"Category Deleted: {catRemoved.mention}\nCategories: {r}\n"
        except StopIteration:
            pass
        
        _ = []
        for role in after.roles:
            if role.name != "@everyone":
                _.append(role.mention)
        r = ", ".join(_)
        try:
            added = iter(role for role in after.roles if role not in before.roles)
            roleAdded = next(added)

            if added:
                embed.description += f"Role Added: {roleAdded.mention}\nRoles: {r}\n"
        except StopIteration:
            pass

        try:
            removed = iter(role for role in before.roles if role not in after.roles)
            roleRemoved = next(removed)
            if removed:
                embed.description += f"Role Removed: {roleRemoved.mention}\nRoles: {r}\n"
        except StopIteration:
            pass
        
        if before.description != after.description:
            embed.description += f"Server Description: ```{before.description}``` -> ```{after.description}```\n"
        
        if before.name != after.name:
            embed.description += f"Server Name: `{before.name}` -> `{after.name}`"
            
        channel = await self.bot.fetch_channel(int(res[0].get("channel_logs")))
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        con = EventDB(self.bot.db)
        res = await con.get(after.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title="Member Updated",
            description=f"Member: {after.mention}\n",
            colour=0x66bb6a
        )
        
        if before.display_name != after.display_name:
            async for log in after.guild.audit_logs(limit=1):
                if log.action == discord.AuditLogAction.member_update:
                    embed.description += f"Member Nick: `{before.display_name}` -> `{after.display_name}`\nChanged By: {log.user.mention}"
        
        _ = []
        for role in after.roles:
            if role.name != "@everyone":
                _.append(role.mention)
        r = ", ".join(_)
        try:
            added = iter(role for role in after.roles if role not in before.roles)
            roleAdded = next(added)
            
            if added:
                embed.description += f"Role Added: {roleAdded.mention}\nRoles: {r}\n"
        except StopIteration:
            pass

        try:
            removed = iter(role for role in before.roles if role not in after.roles)
            roleRemoved = next(removed)
            if removed:
                embed.description += f"Role Removed: {roleRemoved.mention}\nRoles: {r}\n"
        except StopIteration:
            pass
            
        channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_kick(self, guild, user):
        con = EventDB(self.bot.db)
        res = await con.get(guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        async for log in guild.audit_logs(limit=1):
            if log.action == discord.AuditLogAction.kick:
                embed = discord.Embed(
                    title="Member Kicked",
                    description=f"User Kicked: `{user.name}#{user.discriminator}`\Kicked By: `{log.user.mention}`",
                    colour=0xef534e
                )
                
                embed.set_thumbnail(url=str(user.avatar))
                embed.timestamp=datetime.datetime.now()
        
            channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))

            await channel.send(embed=embed)
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        con = EventDB(self.bot.db)
        res = await con.get(guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return

        async for log in guild.audit_logs(limit=1):
            if log.action == discord.AuditLogAction.ban:
                embed = discord.Embed(
                    title="Member Banned",
                    description=f"User Banned: `{user.name}#{user.discriminator}`\nBanned By: `{log.user.mention}`",
                    colour=0xef534e
                )
                
                embed.set_thumbnail(url=str(user.avatar))
                embed.timestamp=datetime.datetime.now()
        
            channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))

            await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        con = EventDB(self.bot.db)
        res = await con.get(member.guild.id)
        con2 = CasesDB(self.bot.db)
        res = await con2.get(member.id, member.guild.id)
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            pass
        else:
            muted_role = self.bot.get_role(await con2.get_muted_role(member.guild.id))
            
            try:
                await member.add_role(muted_role)
            except:
                pass
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title="Member joined!",
            description=f"Member: `{member.name}#{member.discriminator}`\nID: `{member.id}`\nMember Count: `{len(member.guild.members)}`",
            colour=0x66bb6a
        )
        
        embed.set_thumbnail(url=str(member.avatar))
        embed.timestamp=datetime.datetime.now()
        
        channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        con = EventDB(self.bot.db)
        res = await con.get(member.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title="Member left!",
            description=f"Member: `{member.name}#{member.discriminator}`\nID: `{member.id}`\nMember Count: `{len(member.guild.members)}`",
            colour=0xef534e
        )
        
        
        embed.set_thumbnail(url=str(member.avatar))
        embed.timestamp=datetime.datetime.now()
        
        channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))
        
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        con = EventDB(self.bot.db)
        res = await con.get(guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return

        async for log in guild.audit_logs(limit=1):
            if log.action == discord.AuditLogAction.unban:
                embed = discord.Embed(
                    title="Member Unbanned",
                    description=f"User Unbanned: `{user.name}#{user.discriminator}`\nUnbanned By: `{log.user.mention}`",
                    colour=0xef534e
                )
                
                embed.set_thumbnail(url=str(user.avatar))
                embed.timestamp=datetime.datetime.now()
        
            channel = await self.bot.fetch_channel(int(res[0].get("member_logs")))

            await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        con = EventDB(self.bot.db)
        res = await con.get(message.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Message deleted",
            description=f"Channel: {message.channel.mention}\nMessage content: {message.content}",
            colour=0xef534e
        )
        embed.set_thumbnail(url=str(message.author.avatar))
        embed.timestamp=datetime.datetime.now()
        
        channel = await self.bot.fetch_channel(int(res[0].get("message_logs")))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        con = EventDB(self.bot.db)
        res = await con.get(after.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Message Edited",
            description=f"Channel: {after.channel.mention}\nMessage Author: `{after.author.name}#{after.author.discriminator}`\n",
            colour=0xef534e
        )
        
        embed.add_field(name="Before:", value=before.content, inline=False)
        embed.add_field(name="After:", value=after.content, inline=False)
        
        embed.set_thumbnail(url=str(after.author.avatar))
        embed.timestamp=datetime.datetime.now()
        print(res)
        channel = await self.bot.fetch_channel(int(res[0].get("message_logs")))
        
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        con = EventDB(self.bot.db)
        res = await con.get(before.channel.guild.id)
        
        try:
            if res[0].get("member_logs") is None: return
        except Exception:
            return
        
        embed = discord.Embed(
            title=f"Voice Update",
            description=f"Channel: {after.channel.mention}\nMessage Author: `{member.name}#{member.discriminator}`\n",
            colour=0xef534e
        )

        if before.channel != after.channel:
            if after.channel == None:
                embed.description += f"User left voice channel `{before.channel.name}`\n"
            else:
                embed.description += f"Moved Channel: `{before.channel.name}` -> `{after.channel.name}`\n"
        if before.deaf != after.deaf:
            if after.deaf == True:
                embed.description += f"User Deafened"
            else:
                embed.description += f"User Undeafened"
        if before.mute != after.mute:
            if after.deaf == True:
                embed.description += f"User Muted (voice)"
            else:
                embed.description += f"User Unmuted (voice)"

        embed.set_thumbnail(url=str(member.avatar))
        embed.timestamp=datetime.datetime.now()
        
        channel = await self.bot.fetch_channel(int(res[0].get("voice_logs")))
        await channel.send(embed=embed)
        
        
def setup(bot):
    bot.add_cog(Events(bot))
