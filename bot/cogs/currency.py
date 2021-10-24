import random

from bot.tools import Inventory, Items, success, warning, badArg
import discord
from discord.ext import commands


def beg_phrases():
    BEG_PHRASES = {0: "joe biden spat on you",
                   random.randint(20,
                                  60): "joe mama found you on the street and decided to give you {} coins from some of her savings",
                   random.randint(100, 200): "Some rich bozo gave you {} out of pity",
                   -random.randint(12, 50): "You got robbed by some rascal. {}",
                   random.randint(12, 50): "someone threw {} coins at you ",
                   random.randint(1,
                                  100): "You successfully gained {} coins from the act of passively screaming for money "
                                        "whilst reminiscing the quite unsuccessful path you took"}
    money = []
    for money_ in BEG_PHRASES:
        money.append(money_)
    selected_money = random.choice(money)
    return [selected_money, BEG_PHRASES[selected_money]]


class ItemInteractions:
    def __init__(self, economy: Inventory):
        self.economy = economy

    def beg(self, user: discord.Member):
        original_money, phrase = beg_phrases()
        multiplier = round(random.uniform(0.5, 1.2), 2)
        if Items.shiny_hat in self.economy.get_items(user):
            money = round(abs(original_money) * multiplier) + original_money if original_money >= 0 else 0
            if money > 0:
                phrase += f"\n(You got ``{int(multiplier * 100)}%`` more because of the shiny hat!)"
            else:
                phrase = phrase.replace('{}',
                                        f"However, you somehow managed to regain back all the stolen coins with the powers of shiny hat")
            self.economy.deduct_item(Items.shiny_hat, user)
            self.economy.increase_wallet(user.id, money)
            return phrase.replace('{}', f"{original_money}")
        if original_money < 0:
            original_money = self.economy.decrease_wallet(user.id, abs(original_money))
            phrase = phrase.replace('{}', f'They mugged off a grand total of {original_money} coins off you 😞')
        else:
            self.economy.increase_wallet(user.id, original_money)
        return phrase.replace('{}', f"{original_money}")


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy = Inventory()
        self.interactions = ItemInteractions(self.economy)

    @commands.command(aliases=['bal'])
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        await self.economy.send_balance(ctx.author if user is None else user, ctx.channel)

    @balance.error
    async def balance_error(self, ctx, error):
        await badArg(ctx, error, "You need to mention someone to view their balance, silly. To view your balance, just "
                                 "do the command, but without any arguments")

    @commands.command()
    @commands.cooldown(1, random.randint(30, 120))
    async def beg(self, ctx):
        await ctx.send(self.interactions.beg(user=ctx.author))

    @commands.command()
    @commands.cooldown(1, random.randint(60, 120))
    async def rob(self, ctx: commands.Context, user: discord.Member):
        user_money = self.economy.get_wallet(user.id)
        if user_money < 100:
            return await ctx.send(
                embed=discord.Embed(description="This user doesn't have enough money in their wallet, "
                                                "or is too poor, so you are legally obliged by law to not rob them",
                                    colour=0xff0000))
        rob_money = random.randint(1, 83)
        if random.randint(1, 4) != 2:
            amount_taken = self.economy.decrease_wallet(user.id, rob_money)
            self.economy.increase_wallet(ctx.author.id, amount_taken)
            await ctx.send(
                embed=discord.Embed(description=f"Successfully robbed {rob_money} off {user}", colour=0xff0000))
        else:
            dec = random.randint(15, 60)
            amount_decreased = self.economy.decrease_wallet(ctx.author.id, dec)
            self.economy.increase_wallet(user.id, amount_decreased)
            await ctx.send(f"You got caught and {user} spanked you, and took {amount_decreased} coins away with them")

    @commands.command()
    async def shop(self, ctx):
        await self.economy.send_shop(ctx)

    @commands.command()
    async def buy(self, ctx, *, item):
        await self.economy.buy(ctx, item)

    @commands.command()
    async def sell(self, ctx, *, item):
        await self.economy.sell(ctx, item)

    @commands.command(aliases=['in'])
    async def inventory(self, ctx):
        await self.economy.send_inventory(ctx, ctx.author)

    @commands.command()
    async def use(self, ctx, *, item):
        await self.economy.use(ctx, item, ctx.author)

    @commands.command(aliases=['dep', 'transfer'])
    async def deposit(self, ctx, amount):
        if not amount.isdigit() and amount.lower() != 'all':
            return await warning(ctx,
                                 "⚠ You need to provide an amount of money to transfer to the bank. type 'all' instead "
                                 "of an amount to transfer all the money")
        if self.economy.get_bank(user_id=ctx.author.id) >= self.economy.get_bank_limit(user_id=ctx.author.id):
            return await warning(ctx,
                                 "⚠ You **cannot deposit** anymore money into your bank since the **maximum bank limit is reached**. "
                                 "To increase this amount you can either **buy the bank extender** item, or gain it from using other items")
        async with ctx.typing():
            if amount.lower() == 'all':
                transferred = self.economy.transfer_to_bank(ctx.author.id, all_=True)
            else:
                amount = int(amount)
                transferred = self.economy.transfer_to_bank(ctx.author.id, amount)
        await success(ctx, f"Transferred, {transferred} coins to bank.")

    @commands.command(aliases=['take'])
    async def withdraw(self, ctx, amount):
        if not amount.isdigit() and amount.lower() != 'all':
            return await warning(ctx,
                                 "⚠ You need to provide an amount of money to transfer to the bank. type 'all' instead "
                                 "of an amount to transfer all the money")
        async with ctx.typing():
            if amount.lower() == 'all':
                transferred = self.economy.transfer_to_wallet(ctx.author.id, all_=True)
            else:
                amount = int(amount)
                transferred = self.economy.transfer_to_wallet(ctx.author.id, amount)
        await success(ctx, f"Withdrew {transferred} coins from bank to wallet.")


def setup(bot: commands.Bot):
    bot.add_cog(Currency(bot))
