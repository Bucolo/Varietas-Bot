import discord
from discord.ext import commands
import asyncio
from tools import embedbuilder as e, helpembeds as he, components as c
from database import prefix
 
def import_news(ctx):
    with open ("./info/news.txt", "r") as f:
        text = f.read().replace("%prefix%", ctx.prefix)
        return text
 
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # def __init__(self):
    #     super().__init__(
    #         command_attrs={"help": "Show help about the bot, a command, or a category."}
    #     )
    
    @commands.command(description="sends help message", aliases=['hp'])
    async def help(self, ctx, command = None):
        """Get help on any command in the bot"""
        view = c.HelpBase.DropdownView()
        ilink = "https://discord.com/api/oauth2/authorize?client_id=889185777555210281&permissions=8&scope=bot%20applications.commands"
        embed = e.EmbedBuilder(self.bot).build_embed(
            title=f"Help Menu",
            description=f"Invite the bot to your server [here]({ilink})\n"
                        f"Join the support server [here](https://discord.gg/varietas)\n\n"
                        "**Categories:**\n"
                        f"{self.bot.arrow} To view all command categories, click on the **dropdown menu below**!\n\n"
                        "**Guide:**\n"
                        f"{self.bot.arrow} For command categories: Select a category below or do `{ctx.prefix}help <category>`\n"
                        f"{self.bot.arrow} For help with specific commands: do `{ctx.prefix}help <command>`\n\n"
                        f"{self.bot.arrow} If you run into any issues with any commands, feel free to join [the support server](https://discord.gg/varietas) for further assistance!")
        embed.set_footer(text="If the select menu disappears, it simply means the command has timed out. Run the command again to re-use the menu!")
        await ctx.send(embed=embed, view=view)
        
 
def setup(bot:commands.Bot):
    bot.add_cog(Help(bot))