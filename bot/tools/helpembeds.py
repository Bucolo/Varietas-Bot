import discord
from discord.ext import commands
from organiser import get_chunks

class HelpCommand(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot  # type: commands.Bot
        self.all_cmd = {}
        self.main_embed = discord.Embed(color=0xFF8F8F)
        for cmd in self.bot.commands:
            if cmd.cog is None:
                continue
            cog_name = str(cmd.cog.__cog_name__)
            if self.all_cmd.get(cog_name) is None:
                self.all_cmd[cog_name] = {cmd.name: str(cmd.help)}
            else:
                self.all_cmd[cog_name][cmd.name] = str(cmd.help)

    async def callback(self, interaction: discord.Interaction):
        label = interaction.data['values'][0]
        if label.lower() == 'main menu':
            return await interaction.message.edit(embed=self.main_embed)
        embed = self.create_embeds()[label]
        await interaction.message.edit(embed=embed)

    def get_description_embed(self, command: str):
        cmd = self.bot.get_command(command)
        if cmd is not None:
            embed = discord.Embed(colour=0xcc00ff, title=command.upper())
            aliases = str(cmd.aliases).replace("'", '').replace('"', '')
            if self.bot.get_command(command).help is None:
                return discord.Embed(colour=0xff000c, description=f"```fix\nThis command has no description :(```"
                                                                  f"```yaml\nAliases - {aliases if aliases != '[]' else 'None'}```",
                                     title=command)
            embed.description = f"```fix\n{cmd.help}```" \
                                f"```yaml\naliases - {aliases if aliases != '[]' else 'None'}```"
            return embed
        return discord.Embed(colour=0xff0000, title="Invalid",
                             description="This isn't a valid command are you like mentally challenged")

    def merge(self, *mergeCogs: dict):
        """MergeCogs parameter takes in a dict as formatted: {'name for set of commands': [cog_name1, cog_name2, cog_name3...]}"""
        if mergeCogs:
            for mergeCog in mergeCogs:  # merging CMDs from two or more cogs into one name: {'name': 'cog1', 'cog2'...}
                CMDs = {}
                name = list(mergeCog.keys())[0]
                for cog_names in mergeCog[name]:
                    CMDs.update(self.all_cmd[cog_names])
                    del self.all_cmd[cog_names]
                self.all_cmd[name] = CMDs

    def create_embeds(self):
        embeds = {}
        for cog_name in self.all_cmd:
            embed = discord.Embed(colour=0xFF8070, title=cog_name)
            text = []
            for cmd_name in self.all_cmd[cog_name]:
                text.append(f"**{cmd_name}**: ``[{', '.join(self.bot.get_command(cmd_name).aliases)}]``\n")
            text_split = get_chunks(10, text)
            if len(text_split) == 1:
                embed.description = f"🍋\n{''.join(text)}"
                embeds[cog_name] = embed
            else:
                section = 0
                for packet in text_split:
                    section += 1
                    embed.add_field(name=f"Section {section}", value=''.join(packet), inline=True)
                embeds[cog_name] = embed
        return embeds

    async def send_message(self, ctx):
        embeds = self.create_embeds()
        options = [discord.SelectOption(label="Main Menu", emoji='📜')]
        for name in embeds:
            options.append(discord.SelectOption(label=name))
        drop_down = discord.ui.Select(options=options, placeholder="View different categories 📜")
        drop_down.callback = self.callback
        self.add_item(drop_down)
        self.main_embed.set_author(name="My swag commands", icon_url=ctx.author.avatar.url)
        self.main_embed.add_field(name="Info", value="To View the Commands click on the **Dropdown Menu Below**\n"
                                                     "- ``Square brackets = aliases for command name or shortcut name for the command``\n")
        self.main_embed.description = "Watch a tutorial on the bot [here](https://www.youtube.com/watch?v=cvh0nX08nRw).\n" \
                                      "Join my Epico [server](https://discord.gg/hExZSwKqeA)"
        user = self.bot.get_user('add ur user ID')
        self.main_embed.set_footer(text=f"Made by the almighty {user}", icon_url=user.avatar.url)
        await ctx.send(embed=self.main_embed, view=self)
