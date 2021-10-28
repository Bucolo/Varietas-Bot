import discord
from discord.ext import commands
from discord.ui import Button
import datetime
red = 0xff0000
green = 0x00ff00

# Make sure you have a system to catch the checkError to prevent redundant errors:
#     if isinstance(error, commands.errors.CheckFailure):
#         pass

# Do this in the ``async def on_command_error(ctx, error):`` event

def admin():
    """decorator for permissions, so that only admins can access the command"""
    async def predicate(ctx):
        perms = ctx.author.guild_permissions  # type: discord.Permissions
        if not perms.ban_members:
            msg = discord.Embed(description="Peasant, you have no rights of access", color=red)
            msg.set_footer(text="As a wise man once said: 'Do not mess with Varietas'")
            await ctx.send(embed=msg)
            return False
        return True

    return commands.check(predicate)

def mod():
    """decorator for permissions, so that only mods () can access the command"""
    async def predicate(ctx):
        perms = ctx.author.guild_permissions  # type: discord.Permissions
        if not perms.manage_messages:
            msg = discord.Embed(description="Peasant, you have no rights of access", color=red)
            msg.set_footer(text="As a wise man once said: 'Do not mess with Varietas'")
            await ctx.send(embed=msg)
            return False
        return True

    return commands.check(predicate)

def prettify_embed(text, colour=discord.Color.random()):
    embed = discord.Embed(description=text, colour=colour, timestamp=datetime.datetime.utcnow())
    return embed

def get_chunks(interval: int, array: list):
    """split up an array into a two dimensional array with the interval specified"""
    total = []
    a = 0
    if len(array) <= interval:
        return [array]
    for i in range(len(array) // interval):
        chunks = []
        for _ in range(interval):
            chunks.append(array[a])
            a += 1
        total.append(chunks)
    if len(array) % interval != 0:
        total.append(array[a:])
    return total

async def badArg(ctx, error, desc):
    if isinstance(error, commands.MissingRequiredArgument):
        msg = discord.Embed(description=desc, color=red)
        msg.set_footer(text="❌ Missing Required Argument ❌\nYou need a second argument.")
        await ctx.send(embed=msg)
    elif isinstance(error, commands.BadArgument):
        msg = discord.Embed(description=desc, color=red)
        msg.set_footer(text="❌ Bad Argument(s) ❌")
        await ctx.send(embed=msg)

class Paginator(discord.ui.View):
    """circular paginator"""
    def __init__(self, embeds: [discord.Embed], ctx: commands.Context, time_out=60, reply=False):
        super().__init__(timeout=time_out)
        self.embeds = embeds
        self.size = len(embeds)
        self.index = 0
        self.pages.label = f"{self.index+1}/{self.size}"
        self.ctx = ctx
        self.message = None
        self.reply = reply

    async def on_timeout(self) -> None:
        self.previous.disabled = True
        self.next.disabled = True
        await self.message.edit(view=self)

    async def start(self) -> None:
        if self.reply:
            self.message = await self.ctx.reply(embed=self.embeds[self.index], view=self)
        else:
            self.message = await self.ctx.send(embed=self.embeds[self.index], view=self)

    def increment_index(self):
        self.index = (self.index + 1) % self.size

    def decrement_index(self):
        self.index = (self.index - 1) % self.size

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.blurple)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.decrement_index()
        self.pages.label = f"{self.index+1}/{self.size}"
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="", style=discord.ButtonStyle.grey, disabled=True)
    async def pages(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label="➡", style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.increment_index()
        self.pages.label = f"{self.index+1}/{self.size}"
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

class AddButton(discord.ui.View):
    """Useful for adding buttons to a message, and have a callback for it, without having to build it every time.
    Also can use linked buttons."""
    def __init__(self, message: discord.Message, timeout=None, timeout_coroutine=None):
        super().__init__(timeout=timeout)
        self.message = message
        self.timeout_coroutine = timeout_coroutine
        self.buttons = []

    def add_button(self, callback=None, **kwargs):
        button = Button(**kwargs)
        if callback is not None:
            button.callback = callback
        self.buttons.append(button)
        self.add_item(button)

    async def update(self):
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        if self.timeout_coroutine is not None:
            await self.timeout_coroutine
        for button in self.buttons:
            button.disabled = True
        await self.message.edit(view=self)
