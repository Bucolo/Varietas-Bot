import random
import discord
from discord.ext import commands


#  from bot import read, write - **I use local json files to store data, so this will be redundant for dbs**

class Economy:
    """Some discord bot CMDs: rob, beg, shop, buy, work, sell, fight"""

    def __init__(self):
        self.wallet = {}  # read('manage2.json', 'wallet', 1)  # read from database
        self.bank = {}  # read('manage2.json', 'bank', 1)  # read from database
        self.bank_limit = {}  # read('manage2.json', 'bank_limit', 1)  # read from database

    def update(self):  # modify this so it updates the wallet money, bank money, and bank limit of a user with sql
        # eg: def update(self, user_id: int, wallet=None, bank=None, bank_limit=None):
        #         and all ur sql shenanigans here
        """write('manage2.json', self.wallet, 'wallet')
        write('manage2.json', self.bank, 'bank')
        write('manage2.json', self.bank_limit, 'bank_limit')"""

    def get_bank_limit(self, user_id):
        return DEFAULT_BANK_LIMIT if user_id not in self.bank_limit else self.bank_limit[user_id]

    def get_wallet(self, user_id):
        return 0 if self.wallet.get(user_id) is None else self.wallet.get(user_id)

    def get_bank(self, user_id):
        return 0 if self.bank.get(user_id) is None else self.bank.get(user_id)

    def increase_bank_limit(self, user_id):  # write to db
        if user_id not in self.bank_limit:
            self.bank_limit[user_id] = int(DEFAULT_BANK_LIMIT + DEFAULT_BANK_LIMIT * random.uniform(0.07, 0.35))
        else:
            self.bank_limit[user_id] += 1000000 // (self.bank_limit[user_id] * random.uniform(0.33, 2.00))
        self.update()
        return self.bank_limit[user_id]

    def increase_bank(self, user_id: int, amount: int) -> int:  # write to db
        """If the amount to put into bank is exceeding the bank limit, it will send back the amount of money needed
         to put back into the wallet"""
        bank = self.get_bank(user_id)
        bank_limit = self.get_bank_limit(user_id)
        if user_id in self.bank:
            if amount + bank > bank_limit:
                self.bank[user_id] = bank_limit
                self.update()
                return (amount + bank) - bank_limit
            self.bank[user_id] += amount
            self.update()
            return 0
        if amount + bank > bank_limit:
            self.bank[user_id] = bank_limit
            self.update()
            return (amount + bank) - bank_limit
        self.bank[user_id] = amount
        self.update()
        return 0

    def decrease_bank(self, user_id: int, amount) -> int:  # write to db
        if user_id in self.bank:
            bank = self.bank[user_id]
            if amount > bank:
                self.bank[user_id] -= bank
                self.update()
                return bank
            self.bank[user_id] -= amount
            self.update()
            return amount
        self.bank[user_id] = 0
        self.update()
        return 0

    def increase_wallet(self, user_id: int, amount):  # write to db
        self.wallet[user_id] = amount + self.wallet[user_id] if user_id in self.wallet else amount
        self.update()

    def decrease_wallet(self, user_id: int, amount):  # write to db
        if user_id in self.wallet:
            if self.wallet[user_id] - amount < 0:
                self.wallet[user_id] = 0
                amount_decreased = self.wallet[user_id]
                self.wallet[user_id] = 0
                self.update()
                return amount_decreased

            self.wallet[user_id] -= amount
            self.update()
            return amount
        self.wallet[user_id] = 0
        self.update()
        return self.decrease_bank(user_id, amount)

    async def send_balance(self, member: discord.Member, channel: discord.TextChannel):
        async with channel.typing():
            wallet = self.wallet.get(member.id)
            bank = self.bank.get(member.id)
            wallet = 0 if wallet is None else wallet
            bank = 0 if bank is None else bank
            embed = discord.Embed(
                description=f"``wallet``\n```yaml\n🌕 {wallet}```\n``bank``\n```fix\n🌕 {bank}  /  {self.get_bank_limit(user_id=member.id)}```")
            embed.set_author(icon_url=member.avatar.url, name=f"{str(member)}'s current Balance")
        await channel.send(embed=embed)

    def transfer_to_bank(self, user_id: int, amount=0, all_=False) -> int:  # write to db
        """If this function returns false, it indicates that the requested amount to be transferred is higher than the
        actual wallet, so the max amount is transferred. if true, there is no logical error. regardless of which bool
        this returns, the money will still be transferred."""
        wallet = self.get_wallet(user_id)
        if amount > wallet or all_:  # if amount to transfer is larger than the current balance:
            self.decrease_wallet(user_id, wallet)
            bank_leftover = self.increase_bank(user_id, wallet)
            self.increase_wallet(user_id, bank_leftover)
            return wallet - bank_leftover
        self.decrease_wallet(user_id, amount)
        self.increase_bank(user_id, amount)
        return amount

    def transfer_to_wallet(self, user_id: int, amount=0, all_=False) -> int:  # write to db
        """If this function returns false, it indicates that the requested amount to be transferred is higher than the
        actual bank, so the max amount is transferred. if true, there is no logical error. regardless of which bool
        this returns, the money will still be transferred."""
        bank = self.get_bank(user_id)
        if amount > bank or all_:  # if amount to transfer is larger than the current balance:
            self.decrease_bank(user_id, bank)
            self.increase_wallet(user_id, bank)
            return bank
        self.decrease_bank(user_id, amount)
        self.increase_wallet(user_id, amount)
        return amount


class Items:
    """In this class you can make use cmds, that will automatically run when the cmd .use [item] is ran. Just make sure
    to name the async method user_[and the item name (space replaced with underscore)]. so eg:
    if you want to execute a task when the user does .use fried chicken, you create an async method called
    use_fried_chicken(ctx, user), that passes in two arguments (the first is the context, and second is the user)"""
    #  collectibles
    glow_stone = 1
    star = 2
    gold = 3
    silver = 4
    platinum = 5
    shrek = 6
    # tools
    fairy_dust = 7  # Get 100% chance that ur gonna get an item when fishing
    bomb = 8
    bank_extender = 9  # Extends ur bank limit by 7 to 35% on the first time, then by a rational function
    metal_detector = 10
    bank_logger = 13
    fried_chicken = 14
    radioactive_cheese = 15
    shiny_hat = 16  # Automatically used to get more money when begging
    fishing_rod = 17  # Use to find other items: 1 in 75 chance of breaking

    def __init__(self, inventory):
        self.inventory = inventory

    async def use_fishing_rod(self, ctx: commands.Context, user):
        if Items.fishing_rod not in self.inventory.get_items(user):
            return await ctx.send("You don't even have this item 🤡")
        if random.randint(1, 75) == 10:
            self.inventory.deduct_item(Items.fishing_rod, user)
            await ctx.send("Oh no! your fishing rod broke. How unfortunate..")
        else:
            if random.randint(1, 5) == 2 or Items.fairy_dust in self.inventory.get_items(user):
                items = COLLECTIBLES.copy()
                items.extend([Items.bank_extender, Items.bomb, Items.shiny_hat, Items.bank_extender])
                random_item = random.choice(items)
                await ctx.send(f"You obtained a ``{self.inventory.all_items_enum[random_item]}``")
                self.inventory.add_item(random_item, user)
            else:
                await ctx.send("you got attacked by a fish, leaving you no option but to leave promptly..")

    async def use_bomb(self, ctx: commands.Context, user: discord.Member):
        """reign some havoc. Using the bomb will wipe our a portion of some random unlucky person in the server."""
        if Items.bomb not in self.inventory.get_items(user):
            return await ctx.send("You don't even have this item 🤡")
        members = ctx.guild.members
        members.remove(user)
        for member in members:
            if member.bot:
                members.remove(member)
        user = random.choice(members)
        if random.randint(1, 10) != 5:
            victim_money = self.inventory.get_wallet(user.id)
            destroy_money = int(victim_money * (random.randint(20, 60) / 100))
            self.inventory.decrease_wallet(user.id, destroy_money)
            await ctx.send(
                f"You successfully bombed {user.mention}'s wallet, annihilating {destroy_money} coins from them")
        else:
            await ctx.send("Unfortunately, the bomb didn't work. What a tragedy")
        self.inventory.deduct_item(Items.bomb, user)

    async def use_bank_extender(self, ctx: commands.Context, user: discord.Member):
        if Items.bank_extender not in self.inventory.get_items(user):
            return await ctx.send("You don't even have this item 🤡")
        await ctx.send(f"You have successfully used your bank extender, and now can store a max of "
                       f"``{self.inventory.increase_bank_limit(user_id=user.id)} coins``")
        self.inventory.deduct_item(Items.bank_extender, user)

    @staticmethod
    def names():
        """all_items_str has key values of strings, whereas all_items_enum has key values of ints. use this to get
        the name of the item"""
        all_items_str = {}
        all_items_enum = {}
        for name in vars(Items):
            if not name.startswith('__'):
                name_enum = eval(f"{Items.__name__}.{name}")
                if isinstance(name_enum, int):
                    all_items_str[name.replace('_', ' ')] = name_enum
                    all_items_enum[name_enum] = name.replace('_', ' ')
        return all_items_str, all_items_enum


shop_items = {Items.glow_stone: 75000, Items.star: 10000, Items.fairy_dust: 5,
              Items.fishing_rod: 13, Items.fried_chicken: 500, Items.shiny_hat: 10, Items.shrek: 2500, Items.bomb: 50}

COLLECTIBLES = [Items.star, Items.glow_stone, Items.gold, Items.platinum, Items.silver, Items.shrek]


async def warning(ctx, msg):
    await ctx.send(
        embed=discord.Embed(description=msg, colour=0xff0000))


async def success(ctx: commands.Context, msg):
    await ctx.send(
        embed=discord.Embed(description=msg, colour=0x00ff00).set_footer(icon_url=ctx.author.avatar.url))


class Inventory(Economy):
    def __init__(self):
        """self.inventory keeps track of all user's inventory items, and quantity"""
        self.inventory = {}  # read('manage2.json', 'inventory', 2)  # read from database
        self.all_items_str, self.all_items_enum = Items.names()
        self.itemInteractions = Items(self)
        super().__init__()

    async def check_item(self, ctx, item) -> bool:
        item = self.all_items_str.get(item)
        if item is None:
            await warning(ctx, "This is not a valid item in the shop, silly")
            return False
        return True

    def get_items(self, user) -> dict:
        try:
            return self.inventory[user.id]
        except KeyError:
            return {}

    def update_inv(self):
        # do sql db stuff here again like the update method in Economy
        """write('manage2.json', self.inventory, 'inventory')"""

    async def buy(self, ctx: commands.Context, item_name: str):
        if not await self.check_item(ctx, item_name):
            return
        user = ctx.author
        item = self.all_items_str.get(item_name)
        price = shop_items[item]
        if self.get_wallet(user.id) < price:
            return await warning(ctx, "You **do not have enough money** in ``your wallet`` to buy this 👽")
        self.add_item(item, user)
        self.decrease_wallet(user.id, price)
        await success(ctx, f"Successfully bought ``{item_name}`` for ``{price} coins``")

    def add_item(self, item, user):
        """Can parse in the int (enum) value of the item, or the name of the item"""
        if isinstance(item, str):
            item = self.all_items_str[item.lower()]
        if user.id in self.inventory:
            self.inventory[user.id][item] = self.inventory[user.id][item] + 1 if item in self.inventory[user.id] else 1
        else:
            self.inventory[user.id].update({item: 1})
        self.update_inv()

    def deduct_item(self, item, user: discord.Member):
        """Can parse in the int (enum) value of the item, or the name of the item"""
        if isinstance(item, str):
            item = self.all_items_str[item.lower()]
        try:
            if self.inventory[user.id][item] - 1 <= 0:
                del self.inventory[user.id][item]
            else:
                self.inventory[user.id][item] -= 1
            self.update_inv()
            return True
        except KeyError:
            return False

    async def sell(self, ctx: commands.Context, item_name: str):
        if not await self.check_item(ctx, item_name):
            return
        item = self.all_items_str.get(item_name)  # type: int
        price = shop_items[item]
        user = ctx.author
        if self.deduct_item(item, user):
            self.increase_wallet(user.id, price)
            await success(ctx, f"Successfully sold ``{item_name}`` for ``{price} coins``")
            return
        await warning(ctx, "You don't Even have this item 🤦🏻‍♂️")

    async def send_inventory(self, ctx: commands.Context, user: discord.Member):
        userInv = self.get_items(user)
        if not userInv:
            return await warning(ctx, "You do not have anything in your inventory 😞")
        async with ctx.typing():
            user_items = []
            for item in userInv:
                user_items.append(f"```py\n{self.all_items_enum[item]}: {userInv[item]}```")
        await ctx.reply(embed=discord.Embed(title=f"{user}'s Inventory", description=''.join(user_items),
                                            colour=discord.Colour.random()))

    async def send_shop(self, ctx: commands.Context):
        async with ctx.typing():
            items = []
            for item in shop_items:
                items.append(f"{self.all_items_enum[item]}: ``{shop_items[item]}🌕``")
        await ctx.send(embed=discord.Embed(title="Shop items", description='\n'.join(items),
                                           colour=discord.Colour.dark_orange()))

    async def use(self, ctx, item, user):
        item = item.lower()
        method_name = f"use_{item.replace(' ', '_')}"
        if method_name in vars(Items):
            await Items.__getattribute__(self.itemInteractions, method_name)(ctx, user)
        else:
            await warning(ctx, "This isn't a valid item to be used you baboon")


DEFAULT_BANK_LIMIT = 1500
