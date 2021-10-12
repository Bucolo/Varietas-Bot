import discord
from discord.ext import commands

from database import cases
from tools import embedbuilder as e

bot_admins = [839248459704959058, 635971624406876170, 689564113415962717] #Andeh, Erase, Lemony Juicy

class Check:
    
    def botadmin():
        async def botadmincheck(ctx):
            return ctx.author.id in bot_admins
        return commands.check(botadmincheck)
    
    def devserver():
        async def devservercheck(ctx):
            return ctx.guild.id == 872313085455650846
        return commands.check(devservercheck)
    
    def ispremium():
        async def ispremiumcheck(ctx):
            #Do sql search here
            return
        return commands.check(ispremiumcheck)
    
    def canmute():
        async def canmutecheck(ctx):
            is_owner = await ctx.bot.is_owner(ctx.author)
            if ctx.guild is None:
                return False
            if not ctx.author.guild_permissions.manage_roles and not is_owner:
                return False
            if ctx.author in ctx.message.mentions:
                embed = e.EmbedBuilder(ctx.bot).build_embed(
                    title=f"Please don't try to `{ctx.command.name}` yourself!",
                    colour=discord.Colour.red())
                await ctx.message.reply(embed=embed)
                return False
            muted_id = await cases.CasesDB(ctx.bot.db).get_muted_role(ctx.guild.id)
            try:
                muted_id = int(muted_id)
                role = ctx.guild.get_role(muted_id)
                print(role)
                return ctx.author.top_role > role
            except:
                return False
        return commands.check(canmutecheck)
    
class Perms:
    
    def admin():
        async def admincheck(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            else:
                return False
        return commands.check(admincheck)