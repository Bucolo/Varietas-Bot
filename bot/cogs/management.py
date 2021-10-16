import asyncio
import discord
from discord.utils import get
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle
from bot.tools import badArg, mod

def getIdAtSign(text):
    if '@' in text:
        try:
            text = text.split('@&')[1][:len(text.split('@&')[1]) - 1]
            return int(text) if text.isdigit() else text
        except Exception as a:
            print(a)
            return False
    else:
        return int(text) if text.isdigit() else text

async def button_role(guild: discord.Guild, interaction: discord.Interaction, user: discord.Member):
    role = guild.get_role(int(interaction.data['custom_id'].split()[1]))
    if role is None:
        return await interaction.response.send_message(f"⚠ This role is deleted, so I can't add it to you",
                                                       ephemeral=True)
    try:
        if user.get_role(role.id) is None:
            await user.add_roles(role)
            await interaction.message.reply(f"{user.mention} **Added** {role.name} to you", delete_after=5)
        else:
            await user.remove_roles(role)
            await interaction.message.reply(f"{user.mention} **Removed** {role.name} from you", delete_after=5)
    except discord.Forbidden:
        await interaction.response.send_message(
            f"⚠ I couldn't add {role.name} to you since i do not have the perms")

async def menu_role(guild: discord.Guild, interaction: discord.Interaction, user: discord.Member):
    chosen_roles = [guild.get_role(int(role_id.split()[1])) for role_id in interaction.data['values']]
    selects = [guild.get_role(int(select['value'].split()[1])) for select in interaction.message.components[0].to_dict()['components'][0]['options']]
    tasks = []
    for role in selects:
        if role is None:
            await interaction.message.reply(f"Warning: Can't add a role because it doesnt exist anymore..", delete_after=25)
        if role in chosen_roles:
            if user.get_role(role.id) is None:
                tasks.append(user.add_roles(role))
        else:
            if user.get_role(role.id) is not None:
                tasks.append(user.remove_roles(role))
    await interaction.response.defer()
    await asyncio.gather(*tasks)

def getImageLink(text):
    print(text)
    original = text
    text = text.split() if ' ' in text else [text]
    for word in text:
        if word.startswith("http://") or word.startswith("https://"):
            return [original.replace(word, ''), word]  # text and link
    return [original, None]


def splitText2(text: str, symbol='|', text2="Get Your Roles", textMaxLength=700, text2MaxLength=50):
    if symbol in text:
        text, text2 = text.split(symbol)[0], text.split(symbol)[1]
        if len(text) > textMaxLength or len(text2) > text2MaxLength:
            return
        return text, text2
    return text, text2


def is_channel(guild: discord.Guild, channelName: str):
    for channel in guild.channels:
        if channel.name == channelName:
            return True
    return False

async def getRoleAndOther(ctx, bot, splitter='|', test_emoji=False) -> (list, bool, str):
    """'Abort' -> leave,
    False -> try again,
    True -> done,
    [str, int] -> add value"""
    try:
        input_roles = await bot.wait_for("message", check=lambda
            i: i.author.id == ctx.author.id and i.channel.id == ctx.channel.id, timeout=55)
    except asyncio.TimeoutError:
        await ctx.reply("You were too slow. I have to go now!")
        return "Abort"
    if input_roles.content.lower() == 'done':
        return True
    if splitter in input_roles.content:
        other, role = input_roles.content.split(splitter)[0], getIdAtSign(input_roles.content.split(splitter)[1])
        role = get(ctx.guild.roles, id=role)  # type: discord.Role
        if role is None:
            await ctx.send("This is an invalid role. Try again")
            return False
        if not test_emoji:
            if len(other) <= 25:
                return [other, role.id]
            await ctx.send("You cannot have text this large. Try again..")
            return False
        try:
            testing = await ctx.send("testing reaction")
            await testing.add_reaction(other)
            await testing.edit(
                content="✔ this emoji works. Enter 'done' if finished else give me the next reaction role")
        except discord.HTTPException:
            await ctx.send("This is an invalid Emoji, try again")
            return False
        return [other, role.id]
    else:
        await ctx.send(f"You need to split the text and @role/roleID with '{splitter}'.")


class Management(commands.Cog):
    """Managed to find a method to add button and dropdown menu roles without the hassle of storing all the data in a db
    or a local file. the role ID is stored in the component (button/select option) itself, so then the person clicks it,
    it can be retrieved. very neat stuff :()"""
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot

    @commands.command(aliases=['buttonRoles'])
    @mod()
    async def buttonRole(self, ctx, channel: discord.TextChannel, *, text):
        await ctx.send(embed=discord.Embed(
            description="Enter the button text and ping the role you want the the person to get after they react to that button.\n"
                        "Separate this by a '|': EG [click for role|@role1] Enter done when finished",
            color=discord.Colour.dark_magenta()))
        button_roles = discord.ui.View()
        goes = 0
        while 1:
            other_and_role = await getRoleAndOther(ctx, self.bot)
            if other_and_role == 'Abort':
                return
            if other_and_role == True:
                break
            if not other_and_role:
                continue
            button_roles.add_item(
                Button(label=other_and_role[0], style=ButtonStyle.blurple, custom_id=f"button_role {other_and_role[1]}", row=1))
            if goes > 5:
                await ctx.send("You have reached the max amount of button roles for one message.")
                continue
            goes += 1
            await ctx.send("Okay, enter the next button label and role. Enter done when finished")
        if len(button_roles.to_components()) == 0:
            return await ctx.send("You didn't provide me any button texts or roles")
        await ctx.send("Preparing button roles")
        text, imageLink = getImageLink(text)
        embed = discord.Embed(description=text, color=discord.Color.random())
        if imageLink is not None:
            embed.set_image(url=imageLink)
        await channel.send(embed=embed, view=button_roles)

    @buttonRole.error
    async def buttonRoleError(self, ctx, error):
        await badArg(ctx, error,
                     "Try that again but make sure to mention a channel and then the text you want to have "
                     "in the embed of the button role. EG: [buttonrole #channel this is a button role. "
                     "Click the buttons to gain various different roles].\nAfter you specify the channel and text, "
                     "I will ask for the button text and the roles for the buttons.\n"
                     "**You can also add an image link to set an image EG: "
                     "``[buttonRole #channel pick the Bruh roles https://image.png]``")

    @commands.command(aliases=['menuRoles'])
    @mod()
    async def menuRole(self, ctx, channel: discord.TextChannel, *, text):
        text_placeholder = splitText2(text)
        if text_placeholder is None:
            return await ctx.send("The **Embed text is either too big** (max 200 letters) or the **placeholder text is "
                                  "exceeding** the max letters of 50")
        text, placeholder = text_placeholder
        text, imageLink = getImageLink(text)
        await ctx.send(embed=discord.Embed(
            description="Enter the **option text** and **ping the role** you want the the person to get after they react to that emoji.\n"
                        "**Separate this by a '|'**: EG ``[click for role1|@role1]`` Enter **done** when finished",
            color=discord.Colour.dark_magenta()))
        options, goes, one_role = [], 0, False
        while 1:
            other_and_role = await getRoleAndOther(ctx, self.bot)
            if other_and_role == 'Abort':
                return
            if other_and_role == True:
                break
            if not other_and_role:
                continue
            if goes > 11:
                await ctx.send("You have now reached the max amount of menu roles for one message.")
            if goes > 12:
                break
            options.append(discord.SelectOption(label=other_and_role[0], emoji='⚙', value=f"menu_role {other_and_role[1]}"))
            goes += 1
            await ctx.send("Okay, enter the next button label and role. Enter done when finished")
        if not options:
            return await ctx.send("You didn't provide me any menu texts or roles")
        if len(options) != 1:
            await ctx.send("Do you want the user to only retrieve one role from this setup? respond with yes if so..")
            try:
                one_role = (await self.bot.wait_for("message", check=lambda i: i.author == ctx.author, timeout=60)).content
            except asyncio.TimeoutError:
                one_role = 'no'
            one_role = True if "yes" in one_role.lower() else False
        await ctx.send("Preparing Menu roles...")
        max_val = 1 if one_role else len(options)
        embed = discord.Embed(description=text, color=discord.Color.random())
        if imageLink is not None:
            embed.set_image(url=imageLink)
        view = View()
        view.add_item(discord.ui.Select(options=options, min_values=1, max_values=max_val))
        await channel.send(embed=embed, view=view)

    @menuRole.error
    async def menuRoleError(self, ctx, error):
        await badArg(ctx, error,
                     "Try that again but make sure to mention a channel and then the text you want to have "
                     f"in the **embed** of the menu. EG: ``[menurole #channel This is a dropdown Menu role"
                     f"]``.\nAfter you specify the channel and text, "
                     f"I will ask for the select option text and the roles for the option.\n You can also use **|** "
                     f"to split the embed text and the placeholder text\nEG: ``[menurole #channel Bruh|Pick the Bruh roles]``\n"
                     f"**You can also add an image link to set an image EG: "
                     f"``[menurole #channel Bruh|Pick the Bruh roles https://image.png]``")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        guild = interaction.message.guild
        user = interaction.user
        values = interaction.data.get('values')
        custom_id = interaction.data.get('custom_id')
        if custom_id is not None:
            if 'button_role' in custom_id:
                await button_role(guild, interaction, user)
        elif values is not None:
            if 'menu_role' in values[0]:
                await menu_role(guild, interaction, user)

def setup(bot):
    bot.add_cog(Management(bot))
