import asyncpg
import discord

from discord.ext import commands
from discord.flags import Intents

import botconfig
from database import db
import logging
import asyncio
from datetime import datetime

import time
import math
from tools.embedbuilder import EmbedBuilder
import json
loop = asyncio.get_event_loop()
from database.prefix import PrefixDB


async def get_prefix(bot, message):
    con = PrefixDB(bot.db)
    result = await con.get(message.guild.id)
    prefix = commands.when_mentioned_or(result.get("prefix"))(bot, message)
    return prefix


class Varietas(commands.Bot):
    def __init__(self):
        self.__version__ = "0.0.1"
        super().__init__(
            command_prefix=(get_prefix),
            description="A general purpose bot for any server!",
            intents=Intents.all())

        self.db = db.Database()

        self.logger = logging.getLogger(__name__)

    async def _init(self):
        connection = self.db.get_connection()
        self.pool = connection.pool

    async def get_latency(self):
        _ = []

        for x in range(3):
            x = time.time()
            await self.pool.execute("SELECT * FROM latency_test")
            y = time.time()

            _.append(y - x)

        return (_[0] + _[1] + _[2]) / 3


bot = Varietas()


def parsedate(date=None):
    date = datetime.utcnow() if date is None else date
    print(date)
    timestamp = datetime.timestamp(date)
    timestamp = str(timestamp).split('.', 1)[0]
    return f"<t:{timestamp}:F>"

def formatdate(date=None):
    date = datetime.utcnow() if date is None else date
    return date.strftime("%d/%m/%Y %H:%M")

bot.red = discord.Colour.red()
bot.parsedate = parsedate
bot.formatdate = formatdate


@bot.event
async def on_ready():
    exts = [
        "jishaku",
        "cogs.sql",
        "cogs.config",
        "cogs.moderation",
        "cogs.tickets",
        "cogs.events",
        "cogs.automod",
        "cogs.testserver"]

    for e in exts:
        bot.load_extension(e)
    print("Bot is now online")

@bot.event
async def on_command_error(ctx, error):
    #  NEEDS TO HAVE THIS FOR THE CUSTOM DECORATOR TO WORK
    if isinstance(error, commands.errors.CheckFailure):
        pass
    elif isinstance(error, commands.CommandOnCooldown):
        cool_down = f"{round(error.retry_after, 2)}s" if round(error.retry_after, 2) < 60 else f"{error.retry_after // 60} min(s)"
        await ctx.send(embed=discord.Embed(description=f"*Cool-down on command.*\ntry again"
                                                       f" after **{cool_down}**",
                                           color=0xff0000))
    else:
        raise error

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓\n**Latency:** `{round(bot.latency*1000)}ms`\n**PSQL Latency:** `{round(await bot.get_latency()*1000, 2)}ms`")


@bot.command()
async def invite(ctx):
    embed = EmbedBuilder(bot).build_embed(
        title="Click to invite me!",
        url="https://discord.com/api/oauth2/authorize?client_id=883464643304116255&permissions=8&scope=bot",
        timestamp=True)

    await ctx.send(embed=embed)


@bot.command()
async def support(ctx):
    embed = EmbedBuilder(bot).build_embed(
        title="Click to join the support server!",
        url="https://discord.gg/varietas",
        timestamp=True
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def logout(ctx):
    await close_bot()


async def run_bot():
    try:
        bot.pool = await asyncpg.create_pool(botconfig.PSQL_URI)
    except (ConnectionError, asyncpg.exceptions.CannotConnectNowError):
        bot.logger.critical("Could not connect to psql.")

    await bot.start(botconfig.TOKEN)


async def close_bot():
    await bot.pool.close()
    bot.logger.info("Closed psql connection")
    await bot.close()
    bot.logger.info("logged out of bot")
    await bot.http.close()
    bot.logger.info("HTTP Session closed")

    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
        bot.logger.info("Cancelled running task")

try:
    loop.run_until_complete(run_bot())
except KeyboardInterrupt:
    loop.run_until_complete(close_bot())

bot.run(botconfig.TOKEN)
