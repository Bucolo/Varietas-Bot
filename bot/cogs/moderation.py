import discord
from discord.ext import commands
import datetime
from tools import embedbuilder as e, timeInterval
from database import cases
from tools.customchecks import *

from collections import defaultdict


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'
        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
        return ret

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self._databatch = defaultdict(list)
    
    #async def cog_command_error(self, ctx, error):
    #    if isinstance(error, commands.CommandInvokeError):
    #        embed = discord.Embed(
    #            title="An Unexpected Error Occurred!",
    #            description=f"""
    #            ```cmd
    #            {error.original}
    #            ```
    #            """,
    #            colour=0xef534e
    #        )
    #        await ctx.send(embed=embed)
    #    elif isinstance(error, commands.CommandOnCooldown):
    #        embed = discord.Embed(
    #            title="An Unexpected Error Occurred!",
    #            description=f"""
    #            ```cmd
    #            retry after: {error.retry_after} seconds
    #            ```
    #            """,
    #            colour=0xef534e
    #        )
    #        await ctx.send(embed=embed)
    #    else:
    #        embed = discord.Embed(
    #            title="An Unexpected Error Occurred!",
    #            description=f"""
    #            ```cmd
    #            {error.message}
    #            ```
    #            """,
    #            colour=0xef534e
    #        )
    #        await ctx.send(embed=embed)

    @commands.command(slash_command=True, description="ban a user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a user"""
        # Checks to see if the member being banned's top role is higher than
        # the authors role, if it is then dont ban them
        if await role_check(self, ctx, ctx.author, member) is False:
            return
        # Checks to see if the author is trying to ban themselves, if they are
        # then dont ban them
        if await self_check(ctx.author, member) is False:
            return
        # Cleans up the reason if left blank
        reason = "Unspecified" if reason is None else reason
        embed = e.EmbedBuilder(self.bot).build_embed(
            title="You have been banned!",
            description=f"**Server:** {ctx.guild.name}\n"
                        f"**Reason:** {reason}\n"
                        f"**Banned at:** {self.bot.parsedate()}",
            colour=self.bot.red,
            thumb=ctx.guild.icon_url)
        try:
            await member.send(embed=embed)
        except BaseException:
            pass
        await ctx.guild.ban(discord.Object(id=int(member.id)), reason=reason)
        await ctx.message.reply(embed=await conf_embed(self, member, "banned", reason), delete_after=15)
        await ctx.message.delete()

    @commands.command(slash_command=True, description="kick a user")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a user"""
        if await role_check(self, ctx, ctx.author, member) is False:
            return
        if await self_check(self, ctx, ctx.author, member) is False:
            return
        reason = "Unspecified" if reason is None else reason
        embed = e.EmbedBuilder(self.bot).build_embed(
            title="You have been kicked!",
            description=f"**Server:** {ctx.guild.name}\n"
                        f"**Reason:** {reason}\n"
                        f"**Kicked at:** {self.bot.parsedate()}",
            colour=self.bot.red,
            thumb=ctx.guild.icon_url)
        try:
            await member.send(embed=embed)
        except BaseException:
            pass
        await ctx.guild.kick(discord.Object(id=int(member.id)), reason=reason)
        await ctx.message.reply(embed=await conf_embed(self, member, "kicked", reason), delete_after=15)
        await ctx.message.delete()

    @commands.command(slash_command=True, description="unban a user")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason=None):
        """Unban a user"""
        reason = "Unspecified" if reason is None else reason
        await ctx.guild.unban(discord.Object(id=int(member.id)), reason=reason)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"{member} has been unbanned!",
            description=f"**Reason:** {reason}\n"
                        f"**Unbanned at {self.bot.parsedate()}",
            thumb=member.avatar_url)
        await ctx.message.reply(embed=embed, delete_after=15)
        await ctx.message.delete()
        try:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="You have been unbanned!",
                description=f"**Server:** {ctx.guild.name}\n"
                            f"**Reason:** {reason}\n"
                            f"**Unbanned at {self.bot.parsedate()}",
                            thumb=ctx.guild.icon_url)
            await member.send(embed=embed)
        except BaseException:
            return

    @commands.group(aliases=['clear'], invoke_without_command=True, description="purge messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = None):
        """Purge messages"""
        amount = 100 if amount > 100 else amount
        if amount is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide an amount of messages to purge!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author.bot)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Purged {len(deleted)} messages in {ctx.channel.name}!")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command(slash_command=True, description="purge messages from a member")
    @commands.has_permissions(manage_messages=True)
    async def member(self, ctx, member: discord.Member = None, amount: int = None):
        """Purge messages sent by a given member"""
        if member is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide a member to purge their messages!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            return
        if amount is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide an amount of messages to purge!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        amount = 100 if amount > 100 else amount
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author == member)
        embed = e.EmbedBuilder(
            self.bot).build_embed(
            title=f"Cleared {len(deleted)} messages in {ctx.channel.name} from {member}")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command(slash_command=True, description="purge bot messages")
    @commands.has_permissions(manage_messages=True)
    async def bot(self, ctx, amount: int = None):
        """Purge messages sent by bots"""
        if amount is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide an amount of bot messages to purge!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        amount = 100 if amount > 100 else amount
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author == m.author.bot or m.content.startswith('.' or '/' or '-' or '!' or '?' or '+' or ',' or '=' or '$' or '%' or '£'))
        embed = e.EmbedBuilder(
            self.bot).build_embed(
            title=f"Cleared {len(deleted)} bot/command messages {ctx.channel.name}")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command(slash_command=True, description="purge maximum amount of messages (100)")
    @commands.has_permissions(manage_messages=True)
    async def max(self, ctx):
        """Purge maximum amount of messages (100)"""
        await ctx.message.delete()
        await ctx.channel.purge(limit=100)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared 100 messages in {ctx.channel.name}")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command(slash_command=True, description="purge after a message")
    @commands.has_permissions(manage_messages=True)
    async def after(self, ctx, msg_id=None):
        """Delete messages after a given message id"""
        messageDelFrom = await ctx.channel.fetch_message(msg_id)
        await ctx.channel.purge(after=messageDelFrom)
        msg_url = messageDelFrom.jump_url
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared messages in {ctx.channel.name}",
            description=f"[Jump to Message]({msg_url})")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command(slash_command=True, description="purge before a message")
    @commands.has_permissions(manage_messages=True)
    async def before(self, ctx, message_id=None):
        """Purge messages before a given message"""
        messageDelTo = await ctx.chanel.fetch_message(message_id)
        await ctx.channel.purge(before=messageDelTo)
        msg_url = messageDelTo.jump_url
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared messages in {ctx.channel.name}",
            description=f"[Jump to Message]({msg_url})")
        await ctx.send(embed=embed, delete_after=15)

    @commands.group(invoke_without_command=True, description="command group for slowmode")
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, ctx):
        pass
    
    @slowmode.command(slash_command=True, description="enable slowmode in a channel")
    @commands.has_permissions(manage_messages=True)
    async def on(self, ctx, channel: discord.TextChannel = None, time=None):
        """Enable slowmode in a channel."""
        if time is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please enter a time for slow mode to run at",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
        channel = ctx.channel if channel is None else channel
        interval = timeInterval.time_interval(time)
        if interval is not None:
            if interval[1] == "w":
                duration = (interval[0].replace("w", ""))
                TimeInSeconds = int(duration) * 604800
            elif interval[1] == "d":
                duration = (interval[0].replace("d", ""))
                TimeInSeconds = int(duration) * 86400
            elif interval[1] == "h":
                duration = (interval[0].replace("h", ""))
                TimeInSeconds = int(duration) * 3600
            elif interval[1] == "m":
                duration = (interval[0].replace("m", ""))
                TimeInSeconds = int(duration) * 60
            elif interval[1] == "s":
                duration = (interval[0].replace("s", ""))
                TimeInSeconds = int(duration)
            await channel.edit(slowmode_delay=TimeInSeconds)
            embed = e.EmbedBuilder(self.bot).build_embed(
                title=f"Slowmode enabled in {ctx.channel.name} for {interval}")
            await ctx.message.reply(embed=embed, delete_after=15)
            await ctx.message.delete()

    @slowmode.command(slash_command=True, description="disable slowmode in a channel")
    @commands.has_permissions(manage_channels=True)
    async def off(self, ctx, channel: discord.TextChannel = None):
        """Disable slowmode in a channel"""
        channel = ctx.channel if channel is None else channel
        await channel.edit(slowmode_delay=0)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Slowmode disabled in {ctx.channel.name}")
        await ctx.message.reply(embed=embed, delete_after=15)
        await ctx.message.delete()

    @commands.command(slash_command=True, description="Temporarily mute a user.")
    #@Check.canmute()
    async def tempmute(self, ctx, member: discord.Member, duration, *, reason=None):
        """Temporarily mute a user."""
        if reason is None:
            reason = 'Unspecified'
        muted = ctx.guild.get_role(await get_muted_role(self, ctx.guild.id))
        await member.add_roles(muted)
        interval = timeInterval.time_interval(duration)
        current_time = datetime.datetime.utcnow()
        if interval is not None:
            if interval[1] == "w":
                duration = (interval[0].replace("w", ""))
                time_added = datetime.timedelta(weeks=int(duration))
                expirationDate = current_time + time_added
                expirationDate = expirationDate
                timestr = "week" if duration == "1" else "weeks"
            if interval[1] == "d":
                duration = (interval[0].replace("d", ""))
                time_added = datetime.timedelta(days=int(duration))
                expirationDate = current_time + time_added
                expirationDate = expirationDate
                timestr = "day" if duration == "1" else "days"
            if interval[1] == "h":
                duration = (interval[0].replace("h", ""))
                time_added = datetime.timedelta(hours=int(duration))
                expirationDate = current_time + time_added
                expirationDate = expirationDate
                timestr = "hour" if duration == "1" else "hours"
            if interval[1] == "m":
                duration = (interval[0].replace("m", ""))
                time_added = datetime.timedelta(minutes=int(duration))
                expirationDate = current_time + time_added
                expirationDate = expirationDate
                timestr = "minute" if duration == "1" else "minutes"
            if interval[1] == "s":
                duration = (interval[0].replace("s", ""))
                time_added = datetime.timedelta(seconds=int(duration))
                expirationDate = current_time + time_added
                expirationDate = expirationDate
                timestr = "second" if duration == "1" else "seconds"
        else:
            expirationDate = "Never"
        await cases.CasesDB(self.bot.db).case_add("Mute", ctx.guild.id, member.id, reason, str(expirationDate))
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"{member} has been muted",
            description=f"**Duration:** {duration} {timestr}\n**Reason:** {reason}")
        embed.set_footer(text=f"Muted at {self.bot.formatdate()}")
        await ctx.message.reply(embed=embed)
        await ctx.message.delete()
        
        

def setup(bot):
    bot.add_cog(Moderation(bot))

async def get_muted_role(self, guild):
    muted_id = await cases.CasesDB(self.bot.db).get_muted_role(guild)
    try:
        muted_id = int(muted_id)
        return muted_id
    except:
        embed = e.EmbedBuilder(self.bot).build_embed(
            description="Oops! You don't seem to have a muted role on my database, to set one up, either run the `setup muted <role_id>` or `setup muted create`.",
            colour=discord.Colour.red())
        return embed

async def role_check(self, ctx, moderator, member):
    if moderator.top_role > member.top_role:
        return
    if member.top_role > moderator.top_role:
        embed = e.EmbedBuilder(
            self.bot).build_embed(
            title="Oops! Something went wrong.",
            description=f"You can't ban someone with a higher role than you!\n\n"
            f"**{ctx.author.name}'s Top role:** {ctx.author.top_role.mention}\n"
            f"**{member.name}'s Top role:** {member.top_role.mention}",
            colour=self.bot.red)
        await ctx.message.reply(embed=embed, delete_after=10)
        await ctx.message.delete()
        return False


async def self_check(self, ctx, moderator, member):
    if moderator != member:
        return
    elif moderator == member:
        embed = e.EmbedBuilder(
            self.bot).build_embed(
            title="Oops! Something went wrong.",
            description=f"You can't ban yourself! If this was a mistake please make sure you mentioned the right member, or just don't try banning yourself again!",
            colour=self.bot.red)
        await ctx.message.reply(embed=embed, delete_after=10)
        await ctx.message.delete()
        return False


async def conf_embed(self, member, punishment, reason):
    embed = e.EmbedBuilder(self.bot).build_embed(
        title=f"{member} has been {punishment}!",
        description=f"**Reason:** {reason}\n"
                    f"**{punishment} at:** {self.bot.parsedate()}")
    return embed
