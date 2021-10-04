import discord
from discord.ext import commands
import datetime
red = 0xff0000
green = 0x00ff00

# Make sure you have a system to catch the checkError to prevent redundant errors:
#     if isinstance(error, commands.errors.CheckFailure):
#         pass

# Do this in the `async def on_command_error(ctx, error):` event

def admin():
    """decorator for permissions, so that only admins can access the command"""
    async def predicate(ctx):
        print(ctx.author.guild_permissions.administrator)
        if not ctx.author.guild_permissions.administrator:
            msg = discord.Embed(description="Peasant, you have no rights of access", color=red)
            msg.set_footer(text="As a wise man once said: 'Do not mess with the lemony'")
            await ctx.send(embed=msg)
            return False
        return True

    return commands.check(predicate)

def mod():
    """decorator for permissions, so that only mods () can access the command"""
    async def predicate(ctx):
        perms = ctx.author.guild_permissions  # type: discord.Permissions
        if not perms.manage_channels:
            msg = discord.Embed(description="Peasant, you have no rights of access", color=red)
            msg.set_footer(text="As a wise man once said: 'Do not mess with the lemony'")
            await ctx.send(embed=msg)
            return False
        return True

    return commands.check(predicate)

def prettify_embed(text, colour=discord.Color.random()):
    embed = discord.Embed(description=text, colour=colour, timestamp=datetime.datetime.utcnow())
    return embed

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
    """Circular paginator"""
    def __init__(self, embeds: [discord.Embed]):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.size = len(embeds)
        self.index = 0
        self.pages.label = f"{self.index+1}/{self.size}"

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
