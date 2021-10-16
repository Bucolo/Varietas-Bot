import discord
from discord.ext import commands
import datetime
from tools import embedbuilder as e, timeInterval
from database import cases
from bot.tools import mod, admin


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @admin()
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        # Checks to see if the member being banned's top role is higher than
        # the authors role, if it is then dont ban them
        if await self.role_check(ctx, ctx.author, member) is False:
            return
        # Checks to see if the author is trying to ban themselves, if they are
        # then dont ban them
        if await self.self_check(ctx, ctx.author, member) is False:
            return
        # Cleans up the reason if left blank
        reason = "Unspecified" if reason is None else reason
        embed = e.EmbedBuilder(self.bot).build_embed(
            title="You have been banned!",
            description=f"**Server:** {ctx.guild.name}\n"
                        f"**Reason:** {reason}\n"
                        f"**Banned at:** {self.bot.parsedate()}",
            colour=self.bot.red,
            thumb=ctx.guild.icon.url)
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass
        await member.ban(reason=reason)
        await ctx.message.reply(embed=await self.conf_embed(member, "banned", reason), delete_after=15)

    @commands.command()
    @admin()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if await self.role_check(ctx, ctx.author, member) is False:
            return
        if await self.self_check(ctx, ctx.author, member) is False:
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
        except discord.Forbidden:
            pass
        await member.kick(reason=reason)
        await ctx.message.reply(embed=await self.conf_embed(member, "kicked", reason), delete_after=15)
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason=None):
        reason = "Unspecified" if reason is None else reason
        await ctx.guild.unban(discord.Object(id=int(member.id)), reason=reason)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"{member} has been unbanned!",
            description=f"**Reason:** {reason}\n"
                        f"**Unbanned at {self.bot.parsedate()}",
            thumb=member.avatar.url)
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
        except discord.Forbidden:
            return

    @commands.group(aliases=['clear'], invoke_without_command=True)
    @mod()
    async def purge(self, ctx, amount: int = None):
        amount = 100 if amount > 100 else amount
        if amount is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide an amount of messages to purge!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=int(amount))
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Purged {len(deleted)} messages in {ctx.channel.name}!")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command()
    @mod()
    async def member(self, ctx, member: discord.Member = None, amount: int = None):
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

    @purge.command()
    @mod()
    async def bot(self, ctx, amount=None):
        if amount is None:
            embed = e.EmbedBuilder(self.bot).build_embed(
                title="Please provide an amount of bot messages to purge!",
                colour=self.bot.red)
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        amount = 100 if int(amount) > 100 else amount
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author == m.author.bot or m.content.startswith('.' or '/' or '-' or '!' or '?' or '+' or ',' or '=' or '$' or '%' or '£'))
        embed = e.EmbedBuilder(
            self.bot).build_embed(
            title=f"Cleared {len(deleted)} bot/command messages {ctx.channel.name}")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command()
    @mod()
    async def max(self, ctx):
        await ctx.channel.purge(limit=101)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared 100 messages in {ctx.channel.name}")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command()
    @mod()
    async def after(self, ctx, msg_id=None):
        messageDelFrom = await ctx.channel.fetch_message(msg_id)
        await ctx.channel.purge(after=messageDelFrom)
        msg_url = messageDelFrom.jump_url
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared messages in {ctx.channel.name}",
            description=f"[Jump to Message]({msg_url})")
        await ctx.send(embed=embed, delete_after=15)

    @purge.command()
    @mod()
    async def before(self, ctx, msg_id=None):
        messageDelTo = await ctx.chanel.fetch_message(msg_id)
        await ctx.channel.purge(before=messageDelTo)
        msg_url = messageDelTo.jump_url
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Cleared messages in {ctx.channel.name}",
            description=f"[Jump to Message]({msg_url})")
        await ctx.send(embed=embed, delete_after=15)

    @commands.group(invoke_without_command=True)
    @mod()
    async def slowmode(self, ctx, channel: discord.TextChannel = None, time=None):
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

    @slowmode.command()
    @mod()
    async def off(self, ctx, channel: discord.TextChannel = None):
        channel = ctx.channel if channel is None else channel
        await channel.edit(slowmode_delay=0)
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Slowmode disabled in {ctx.channel.name}")
        await ctx.message.reply(embed=embed, delete_after=15)
        await ctx.message.delete()

    @commands.command()
    @mod()
    async def tempmute(self, ctx, member: discord.Member, duration, *, reason=None):
        reason = "Unspecified" if reason is None else reason
        interval = timeInterval.time_interval(duration)
        current_time = datetime.datetime.utcnow()
        if interval is not None:
            if interval[1] == "w":
                duration = (interval[0].replace("w", ""))
                time_added = datetime.timedelta(weeks=int(duration))
                expirationDate = current_time + time_added
                finalExpirationDate = self.bot.formatdate(expirationDate)
                timestr = "week" if duration == "1" else "weeks"
            if interval[1] == "d":
                duration = (interval[0].replace("d", ""))
                time_added = datetime.timedelta(days=int(duration))
                expirationDate = current_time + time_added
                finalExpirationDate = self.bot.formatdate(expirationDate)
                timestr = "day" if duration == "1" else "days"
            if interval[1] == "h":
                duration = (interval[0].replace("h", ""))
                time_added = datetime.timedelta(hours=int(duration))
                expirationDate = current_time + time_added
                finalExpirationDate = self.bot.formatdate(expirationDate)
                timestr = "hour" if duration == "1" else "hours"
            if interval[1] == "m":
                duration = (interval[0].replace("m", ""))
                time_added = datetime.timedelta(minutes=int(duration))
                expirationDate = current_time + time_added
                finalExpirationDate = self.bot.formatdate(expirationDate)
                timestr = "minute" if duration == "1" else "minutes"
            if interval[1] == "s":
                duration = (interval[0].replace("s", ""))
                time_added = datetime.timedelta(seconds=int(duration))
                expirationDate = current_time + time_added
                finalExpirationDate = self.bot.formatdate(expirationDate)
                timestr = "second" if duration == "1" else "seconds"
        else:
            finalExpirationDate = "Never"
        confirmEmbed = discord.Embed(description=f"**Duration:** {duration} {timestr}\n**Reason:** {reason}",
                                    colour=discord.Colour.red())
        confirmEmbed.set_author(name=f"{member} has been muted")
        mutedRoleID = await self.get_muted_role(ctx.guild, ctx)
        mutedRole = ctx.guild.get_role(mutedRoleID)
        await cases.CasesDB(self.bot.db).case_add("Mute", ctx.guild.id, member.id, reason, finalExpirationDate)
        await member.add_roles(mutedRole)
        await ctx.message.reply(embed=confirmEmbed)
        await ctx.message.delete()

    async def get_muted_role(self, guild, ctx):
        muted_id = await cases.CasesDB(self.bot.db).get_muted_role(guild.id)
        try:
            muted_id = int(muted_id)
            return muted_id
        except:
            embed = e.EmbedBuilder(self.bot).build_embed(
                description="Oops! You don't seem to have a muted role on my database, to set one up, either run the `setup muted <role_id>` or `setup muted create`.",
                colour=discord.Colour.red())
            await ctx.message.reply(embed=embed)

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
                description=f"You can't ban yourself! If this was a mistake please make sure you mentioned the right member, "
                            f"or just don't try banning yourself again!",
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

def setup(bot):
    bot.add_cog(Moderation(bot))
