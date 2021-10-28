from discord.ext import commands
from bot.tools import helpembeds as he
 
def import_news(ctx):
    with open("./info/news.txt", "r") as f:
        text = f.read().replace("%prefix%", ctx.prefix)
        return text
 
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Help(self, ctx: commands.Context, *, command=None):
        help_cmd = he.HelpCommand(self.bot)
        if command is not None:
            print(self.bot.get_command('manage'))
            description = help_cmd.get_description_embed(command)
            return await ctx.send(embed=description)
        help_cmd.merge({'Fun': ['Miscellaneous', 'Fun', 'WebScraping']},
                       {'Moderation': ['Management', 'Moderation']})
        await help_cmd.send_message(ctx)

def setup(bot:commands.Bot):
    bot.add_cog(Help(bot))