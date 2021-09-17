import discord
from discord.ext import commands
import string
import random
import json

from database.ticket import TicketDB
from tools.embedbuilder import EmbedBuilder
from database.automod import AutoModDB
from database.prefix import PrefixDB


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e = EmbedBuilder(self.bot)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        if str(payload.emoji) == "❌":
            chan = self.bot.get_channel(int(payload.channel_id))
            await chan.delete(reason="Ticket Closed")
            return
        content = await TicketDB(self.bot.db).get(payload.message_id)
        # await self.bot.get_channel(payload.channel_id).send(content)

        if len(content) <= 0:
            return

        cat = self.bot.get_channel(int(content[0]["category"]))
        if cat is None:
            return

        roles = content[0]["roles"]
        overwrites = {
            payload.guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
            )
        }

        roles.strip("][").split(", ")

        for role in roles:
            role = payload.guild.get_role(int(role))
            overwrites[role.name] = discord.PermissionsOverwrite(
                read_message=True,
                send_messages=True
            )

        letters = string.ascii_letters
        id = "".join(random.choice(letters) for i in range(15))
        taken = await TicketDB(self.bot.db).get_code(id)
        if len(taken) > 0:
            while len(taken) > 0:
                id = "".join(random.choice(letters) for i in range(15))
                taken = await TicketDB(self.bot.db).get_code(id)

        await TicketDB(self.bot.db).set_code(200, id)

        channel = await cat.create_text_channel(
            name=f"ticket-{id}",
            overwrites=overwrites
        )

        m = await channel.send(embed=self.e.build_embed(
            title="Ticket Opened!",
            description="To close the ticket, press the close button below."
        ))

        m.add_reaction("❌")

    @commands.Cog.listener()
    async def on_message(self, message):
        x = await AutoModDB(self.bot.db).get(message.guild.id)

        msg = message.content.strip("**")

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
            
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        con = PrefixDB(self.bot.db)
        await con.remove(guild.id)


def setup(bot):
    bot.add_cog(Events(bot))
