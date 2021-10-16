import discord
from discord.ext import commands, menus
import datetime

from tools.embedbuilder import EmbedBuilder as e
from tools.components import Avatar
from tools.paginator import inrole

e_DiscordStaff = '<:discordStaff:875924809660366848>'
e_DiscordPartner = '<:partner:875924876555329556>'
e_HypeSquad = '<:hypesquad:875924906817241128>'
e_BugHunter = '<:BugHunter:875924938786226247>'
e_HSBravery = '<:HypeSquadBravery:875924968360267786>'
e_HSBrilliance = '<:HypeSquadBrilliance:875924996172693514>'
e_HSBalance = '<:HypeSquadBalance:875925025260191865>'
e_EarlySupporter = '<:BadgeEarlySupporter:875925050816090163>'
e_VerifiedBotDev = '<:BadgeVerifiedBotDeveloper:875925078141976607>'
e_BugHunter2 = '<:BugHunterLvl2:875925118088511488>'
e_VerifiedBot = '<:discordVerifiedBot:875925159263993867>'
e_arrow = "<a:arrow:882812954314154045>"

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, member: discord.Member=None):
        member = ctx.author if member is None else member
        embed = e(self.bot).build_embed(
            title=f"{member}'s Avatar", colour=member.colour)
        view = Avatar(member.avatar.url, member)
        embed.set_image(url=member.avatar.url)
        await ctx.message.reply(embed=embed, view=view)
        
    @commands.command(aliases=['ri'])
    async def roleinfo(self, ctx, role: discord.Role, *, feature=None):
        roleID = role.id
        roleName = role.name
        roleColour = role.colour
        roleMention = f"<@&{role.id}>"
        roleHoisted = "Yes" if role.hoist else "No"
        rolePos = role.position
        roleMentionable = "Yes" if role.mentionable else "No"
        roleCreated = role.created_at.strftime("%d/%m/%Y %H:%M:%S")
        
        keyPerms = ["administrator", "ban_members", "deafen_members",
                    "kick_members", "manage_channels", "manage_emojis",
                    "manage_guild", "manage_messages", "manage_nicknames",
                    "manage_permissions", "manage_roles", "manage_webhooks",
                    "mention_everyone", "move_members", "mute_members",
                    "view_audit_log"]
        Permissions = []
        if role.permissions.administrator:
            Permissions.append("Administrator")
        if role.permissions.ban_members:
            Permissions.append("Ban Members")
        if role.permissions.deafen_members:
            Permissions.append("Server Deafen Members")
        if role.permissions.kick_members:
            Permissions.append("Kick Members")
        if role.permissions.manage_channels:
            Permissions.append("Manage Channels")
        if role.permissions.manage_emojis:
            Permissions.append("Manage Emojis")
        if role.permissions.manage_guild:
            Permissions.append("Manage Server")
        if role.permissions.manage_messages:
            Permissions.append("Manage Messages")
        if role.permissions.manage_nicknames:
            Permissions.append("Manage Nicknames")
        if role.permissions.manage_permissions:
            Permissions.append("Manage Permissions")
        if role.permissions.manage_roles:
            Permissions.append("Manage Roles")
        if role.permissions.manage_webhooks:
            Permissions.append("Manage Webhooks")
        if role.permissions.mention_everyone:
            Permissions.append("Mention Everyone")
        if role.permissions.move_members:
            Permissions.append("Move Members")
        if role.permissions.mute_members:
            Permissions.append("Server Mute Members")
        if role.permissions.view_audit_log:
            Permissions.append("View Audit Log")
        Permissions = str(Permissions)
        Permissions = Permissions.replace("'", "").replace("[", "").replace("]", "")
        if feature is None:
            embed = discord.Embed(colour=roleColour)
            embed.set_footer(text=f"Role Created • {roleCreated}")
            fields = [("ID", roleID, True),
                      ("Name", roleName, True),
                      ("Colour", roleColour, True),
                      ("Mention", roleMention, True),
                      ("Hoisted?", roleHoisted, True),
                      ("Position", rolePos, True),
                      ("Mentionable?", roleMentionable, True),
                      ("Important Role Permissions", Permissions, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await ctx.message.reply(embed=embed)
            
    @commands.command(aliases=['si'])
    async def serverinfo(self, ctx):
        embed = discord.Embed(colour=ctx.guild.owner.colour,
                        timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=f"{ctx.guild.name} Server Information")
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]
        fields = [("Owner:", ctx.guild.owner, True),
                ("Region:", ctx.guild.region, True),
                ("Created At:", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                ("Members:", len(ctx.guild.members), True),
                ("Banned Members:", len(await ctx.guild.bans()), True),
                ("Roles:", len(ctx.guild.roles), True),
                ("Channel Categories:", len(ctx.guild.categories), True),
                ("Text Channels:", len(ctx.guild.text_channels), True),
                ("Voice Channels:", len(ctx.guild.voice_channels), True),
                ("Nitro Boosts", ctx.guild.premium_subscription_count, True),
                ("Nitro Booster Level", ctx.guild.premium_tier, True),
                ("Invites", len(await ctx.guild.invites()), True),
                ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", False),
                ("\u200b", "\u200b", True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.message.reply(embed=embed)
        
    @commands.command(aliases=['rolememberinfo', 'rmi', 'ir'])
    async def inrole(self, ctx, *, role: discord.Role):
        if role is None:
            embed = discord.Embed(title="Please enter a role",
                                  colour=discord.Colour.red())
            await ctx.message.reply(embed=embed, delete_after=10)
            await ctx.message.delete()
            return
        guild = self.bot.get_guild(ctx.guild.id)
        members = []
        for member in guild.members:
            if role in member.roles:
                members.append(f"`{member}`")
        amount = len(members)
        if amount == 0:
            members = ["No users in this role."]
        items = members
        menu = menus.MenuPages(inrole(items, role, amount))
        await menu.start(ctx)
        
    @commands.command(aliases=['ui', 'whois'])
    async def userinfo(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        name, disc, nick, botStr, colour, status, created, joined, topRole, activity = member.name, member.discriminator, member.display_name, "Bot" if member.bot else "Human", member.colour, member.status, self.bot.parsedate(member.created_at), self.bot.parsedate(member.joined_at), member.top_role.mention, member.activity
        if member.premium_since is None:
            boosted_since = "Not boosting"
        else:
            boosted_since = self.bot.parsedate(member.premium_since)
        if str(status) == "dnd":
            statusStr = "🔴 DND"
        elif str(status) == "online":
            statusStr = "🟢 Online"
        elif str(status) == "offline":
            statusStr = "⚫ Offline"
        elif str(status) == "idle":
            statusStr = "🟠 Idle"
        elif str(status) == "streaming":
            statusStr = "🟣 Streaming"
        nick = "None" if name == nick else nick
        badges_str = ""
        badges = member.public_flags
        if badges.staff:
            badges_str += f"{e_DiscordStaff} "
        if badges.partner:
            badges_str += f"{e_DiscordPartner} "
        if badges.hypesquad:
            badges_str += f"{e_HypeSquad} "
        if badges.bug_hunter:
            badges_str += f"{e_BugHunter} "
        if badges.hypesquad_bravery:
            badges_str += f"{e_HSBravery} "
        if badges.hypesquad_brilliance:
            badges_str += f"{e_HSBrilliance} "
        if badges.hypesquad_balance:
            badges_str += f"{e_HSBalance} "
        if badges.early_supporter:
            badges_str += f"{e_EarlySupporter} "
        if badges.verified_bot_developer:
            badges_str += f"{e_VerifiedBotDev} "
        if badges.bug_hunter_level_2:
            badges_str += f"{e_BugHunter2} "
        if badges.verified_bot:
            badges_str += f"{e_VerifiedBot} "
        if len(member.roles[1:]) > 0:
            roles_list = []
            for role in member.roles[1:]:
                roles_list.append(role.mention) 
            roles = ", ".join(reversed(roles_list))
            roles_amount = len(member.roles[1:])
        else:
            roles = "User has no roles"
            roles_amount = 0
            topRole = "User has no roles."
        if not member.joined_at:
            position = "Couldn't retrieve user position."
        else:
            position = sum(
                m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None) + 1
            last_digit = position % 10
            if last_digit == 1:
                indicator = "st"
            elif last_digit == 2:
                indicator = "nd"
            elif last_digit == 3:
                indicator = "rd"
            else:
                indicator = "th"
        if activity:
            if type(activity) == discord.Spotify:
                activity_str = f'Listening [{activity.title} - {activity.artist}](https://open.spotify.com/track/{activity.track_id})'
            elif str(activity.type) == "ActivityType.custom":
                activity_str = str(activity)
            elif str(activity.type) == "ActivityType.unknown":
                pass
            else:
                activity_type_list = str(activity.type).split(".")
                activity_str = f"{activity_type_list[1].capitalize()} {activity.name}"
        else:
            activity_str = ""
        embed = discord.Embed(description=f"{activity_str}\n{badges_str}",
                              colour=member.colour)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=str(member), icon_url=str(member.avatar.url))
        fields = [("Account Created", str(created), True),
                  (f"Joined {ctx.guild.name}", str(joined), True),
                  ("Boosting Since", str(boosted_since), True),
                  ("Nickname", str(nick), True),
                  ("Discriminator", str(disc), True),
                  ("User Type", str(botStr), True),
                  ("Status", str(statusStr), True),
                  ("User Colour", str(member.colour), True),
                  ("User ID", str(member.id), True),
                  ("Highest Role", str(topRole), True),
                  ("Number of Roles", str(roles_amount), True),
                  ("Roles", roles, False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=f"{str(position)}{indicator} member to join")
        await ctx.message.reply(embed=embed)
        
def setup(bot):
    bot.add_cog(Miscellaneous(bot))