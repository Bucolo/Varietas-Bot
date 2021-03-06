import discord
import datetime

class EmbedBuilder:
    def __init__(self, bot):
        self.embed = discord.Embed()
        self.bot = bot

    def build_embed(self, title="", description="", colour=0x66bb6a, thumb="", image="", timestamp=False, url=""):
        self.embed.title = title
        self.embed.description = description
        self.embed.colour = colour

        self.embed.set_thumbnail(url=thumb) if thumb != "" else None
        self.embed.set_image(url=image) if image != "" else None
        self.embed.url=url if url != "" else None
        if timestamp:
            self.embed.timestamp = datetime.datetime.now()

        self.embed.set_footer(
            text=(f"Join the support server! discord.gg/varietas"),
            icon_url=str(self.bot.user.avatar)
        )

        return self.embed