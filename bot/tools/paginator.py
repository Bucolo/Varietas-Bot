import discord
from discord.ext import menus

class inrole(menus.ListPageSource):
    def __init__(self, members, role, amount):
        super().__init__(entries=members, per_page=20)
        self.role = role
        self.amount = amount
    
    async def format_page(self, menu, item):
        client = menu.ctx.bot
        role = self.role
        amount = self.amount
        
        items = []
        for element in item:
            if element not in [role, amount]:
                items.append(element)
                
        joined_members = "\n".join(items)
        
        embed = discord.Embed(title=f"Members with {role.name} ({amount})",
                              description=f"{joined_members}",
                              colour=role.colour)
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed