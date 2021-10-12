import asyncio
import json
import random
import discord
from discord import ButtonStyle
from discord.ui import Button, View
import time
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from Organiser import badArg, Paginator

greetings = ['yo', 'im the biggus bot', 'My aim is simple; Lemon World Supremacy', "Don't eat spaghetti without sauce",
             "that's kinda sussy", "I'm absorbing my citric acid to gain unlimited powers",
             "Jeff Bezos is an intergalactic space probe in the form of a human.",
             "What do you call a man with no knees?\nKneel!",
             "Epic rofl moment"]

font = {'q': '𝗾', 'w': '𝘄', 'e': '𝗲', 'r': '𝗿', 't': '𝘁', 'y': '𝘆', 'u': '𝘂', 'i': '𝗶', 'o': '𝗼', 'p': '𝗽',
        'a': '𝗮', 's': '𝘀', 'd': '𝗱', 'f': '𝗳',
        'g': '𝗴', 'h': '𝗵', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'z': '𝘇', 'x': '𝘅', 'c': '𝗰', 'v': '𝘃', 'b': '𝗯',
        'n': '𝗻', 'm': '𝗺'}

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"
}

headers2 = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, '
                          'like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53.'}

reactions = '⬅️ ➡️'.split()


def convertSoup(link, user_agent=None):
    if user_agent is not None:
        return BeautifulSoup(requests.get(link, headers=user_agent, timeout=5).content, 'html.parser')
    page = requests.get(link, timeout=5)
    return BeautifulSoup(page.content, 'html.parser')


def add_sub(react):
    react = str(react)
    if react == reactions[0]:
        return -1
    elif react == reactions[1]:
        return 1
    else:
        return 0


def accuracy(sentence, userInput):
    words = sentence.split()
    sentence = ''.join(words)
    userInput = userInput.split()
    correct = 1
    for i in range(len(words)):
        try:
            for a in range(len(words[i])):
                try:
                    correct += 0 if words[i][a] != userInput[i][a] else 1
                except IndexError:
                    break
        except IndexError:
            break
    return round(correct / len(sentence) * 100, 2)


def convertFont(string):
    new = ''
    for char in string:
        if char in font:
            new += font[char]
        elif char.isupper() and char.lower() in font:
            new += font[char.lower()].upper()
        else:
            new += char
    return new


def arrowButton(index, length, disabled1=False, disabled2=False):
    view = View()
    if disabled1 and disabled2:
        view.add_item(Button(label='⬅')),
        view.add_item(Button(style=ButtonStyle.grey, label=f"{index}/{length}", disabled=True))
        view.add_item(Button(style=ButtonStyle.green, label='➡', disabled=True))
        return view
    if disabled1:
        view.add_item(Button(style=ButtonStyle.grey, label='⬅', disabled=True))
        view.add_item(Button(style=ButtonStyle.grey, label=f"{index}/{length}", disabled=True))
        view.add_item(Button(style=ButtonStyle.green, label='➡'))
        return view

    if disabled2:
        view.add_item(Button(style=ButtonStyle.green, label='⬅'))
        view.add_item(Button(style=ButtonStyle.grey, label=f"{index}/{length}", disabled=True))
        view.add_item(Button(style=ButtonStyle.grey, label='➡', disabled=True))
        return view

    view.add_item(Button(style=ButtonStyle.green, label='⬅'))
    view.add_item(Button(style=ButtonStyle.grey, label=f"{index}/{length}", disabled=True))
    view.add_item(Button(style=ButtonStyle.green, label='➡'))
    return view


def oldChatBotReply(message):
    url = "https://robomatic-ai.p.rapidapi.com/api.php"
    payload = f"key=RHMN5hnQ4wTYZBGCF3dfxzypt68rVP&cbid=1&ChatSource=RapidAPI&SessionID=RapidAPI1&cbot=1&op=in&in={message}"
    headersRoboMatic = {
        'content-type': "application/x-www-form-urlencoded",
        'x-rapidapi-host': "robomatic-ai.p.rapidapi.com",
        'x-rapidapi-key': "c97af16bb5msh4a9c4bd102924e7p13f694jsna81d3f25137a"
    }
    response = requests.request("POST", url, data=payload, headers=headersRoboMatic)
    try:
        print(response.text, "\nRoboMatic")
        return json.loads(response.text).get('out')
    except json.decoder.JSONDecodeError:
        return random.choice(greetings)


def chatBotReply(message):
    message = message.replace("lemony", 'aco')
    if random.randint(1, 5) == 4:
        return random.choice(greetings)
    url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"
    querystring = {"bid": "178", "key": "sX5A2PcYZbsN5EY6", "uid": "mashape", "msg": f"{message}"}
    headersBrainShop = {
        'x-rapidapi-host': "acobot-brainshop-ai-v1.p.rapidapi.com",
        'x-rapidapi-key': "c97af16bb5msh4a9c4bd102924e7p13f694jsna81d3f25137a"
    }
    response = requests.request("GET", url, headers=headersBrainShop, params=querystring)
    print(response.text, "\nBrainShop")
    output = json.loads(response.text)['cnt']
    return output if output is not None else oldChatBotReply(message)


class WebScraping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['w'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, query):
        url = "https://community-open-weather-map.p.rapidapi.com/weather"

        querystring = {"q": query, "lat": "0", "lon": "0", "id": "2172797", "lang": "null",
                       "units": "\"metric\" or \"imperial\"", "mode": "xml, html"}
        h = {
            'x-rapidapi-key': "c97af16bb5msh4a9c4bd102924e7p13f694jsna81d3f25137a",
            'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
        }
        response = json.loads(requests.request("GET", url, headers=h, params=querystring).text)
        if response.get('message'):
            await ctx.send(embed=discord.Embed(description="Bruh there were no result for this place", color=0xff0000))
        feels_like = round(float(response['main']['feels_like']) - 273.15, 2)
        temp = round(float(response['main']['temp']) - 273.15, 2)
        maxT, minT = round(float(response['main']['temp_max']) - 273.15, 2), round(
            float(response['main']['temp_min']) - 273.15, 2)
        wind = response['wind']
        misc = f"-The current air pressure is {response['main']['pressure']} Pa\n-The Humidity is {response['main']['humidity']}%" \
               f"\n-The Visibility is {int(response['visibility']) / 1000} Km"
        embed = discord.Embed(color=discord.Color.random(), title=f"{response['name']}, {response['sys']['country']}")
        embed.add_field(name="Weather", value=f"-{response['weather'][0]['description']}\n{misc}")
        embed.add_field(name="Wind & Temperature",
                        value=f"🌡 **{temp}℃** (max: {maxT}℃, min: {minT}℃)\n👐 Feels like **{feels_like}℃**\n🌬 Wind Speed: "
                              f"**{wind['speed']}mph**", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['i'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def image(self, ctx, *, query):
        if ctx.channel.nsfw:
            url = f"https://www.google.com/search?q={query}&hl=en&sxsrf=ALeKk02wVcYA5Sbg-fi9m3uEVT2ly_X8Zg:1622576889463&source=lnms&tbm=isch&sa=X&ved=2ahUKEwixtff4mffwAhUlwAIHHRQIAcAQ_AUoAXoECAEQAw&biw=1536&bih=754"
        else:
            url = f"https://www.google.com/search?q={query}&hl=en&safe=on&sxsrf=ALeKk02wVcYA5Sbg-fi9m3uEVT2ly_X8Zg:1622576889463&source=lnms&tbm=isch&sa=X&ved=2ahUKEwixtff4mffwAhUlwAIHHRQIAcAQ_AUoAXoECAEQAw&biw=1536&bih=754"
        async with ctx.typing():
            soup = convertSoup(url, headers2)
            images = soup.findAll('a', class_='wXeWr islib nfEiy')
            all_links = []
            counter = 0
            for link in images:
                if counter > random.randint(20, 30):
                    break
                try:
                    all_links.append(link.find('img')['data-src'])
                    counter += 1
                except KeyError:
                    continue
            if len(all_links) == 0:
                return await ctx.reply("No results were found :()")
        embeds = []
        for img_url in all_links:
            embeds.append(
                discord.Embed(color=discord.Color.random()).set_author(name="Here is your Image",
                                                                       icon_url=ctx.author.avatar.url).set_image(
                    url=img_url).set_footer(text=f"search query: {query}"))
        await ctx.reply(embed=embeds[0], view=Paginator(embeds))

    @image.error
    async def imageError(self, ctx, error):
        await badArg(ctx, error, f"Search an image online. You have to include a query. eg: .i tree]")

    @commands.command(aliases=['typeTest', 'wordsPerMinute'])
    async def wpm(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        soup = convertSoup('https://www.bestrandoms.com/random-sentence', headers)
        sentence = soup.find(class_='font-18').text
        embed = discord.Embed(description=convertFont(sentence), color=discord.Color.random())
        embed.set_author(name="Typing Test wpm", icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Type in the sentence above as quick as possible")
        await ctx.send(embed=embed)
        await asyncio.sleep(0.5)
        begin = time.time()
        try:
            userInput = (await self.bot.wait_for('message', check=check, timeout=160)).content
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention} You took too long!")
        if userInput == convertFont(sentence):
            return await ctx.send("Bruh you just copy pasted it I'm not stupid")
        if ' ' not in userInput:
            return await ctx.send("You did shit at the wpm test. That's all I gotta say")
        timeTaken = round(time.time() - begin, 2)
        sentence, userInput = sentence.lower(), userInput.lower()
        a = accuracy(sentence, userInput)
        userWords = len(userInput.split()) if ' ' in userInput else 1
        userLetters = len(userInput)
        await ctx.send(embed=discord.Embed(color=0xffff09,
                                           description=f"-You took **{timeTaken}** seconds with an accuracy of **{a}%**\n"
                                                       f"-About **{round((60 / timeTaken) * userWords, 1)}** words per minute\n"
                                                       f"-Or **{round(userLetters / timeTaken, 3)}** Letters per second"))

    @commands.command()
    async def joke(self, ctx):
        soup = convertSoup('https://www.bestrandoms.com/random-jokes', headers)
        allJokes = soup.find(class_='content').findAll(class_='font-18')

        joke = allJokes[random.randint(1, 7)].text[3:]
        joke = joke.replace('?', '?\n')
        await ctx.send(embed=discord.Embed(description=joke, color=discord.Color.random()))

    @commands.command()
    async def qr(self, ctx, *, data):
        if ' ' in data:
            data = '%20'.join(data.split())
        embed = discord.Embed(title='The biggus Quick Response code', color=0xc349d6)
        embed.set_image(url='https://chart.apis.google.com/chart?cht=qr&chs=200x200&chld=L|0&chl=' + data)
        await ctx.send(embed=embed)

    @qr.error
    async def qrError(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            data = 'https://www.youtube.com/watch?v=SwBEZhb4NVA'
            embed = discord.Embed(title="You're meant to include ASCII", color=0xff0000)
            embed.set_image(url='http://chart.apis.google.com/chart?cht=qr&chs=200x200&chld=L|0&chl=' + data)
            embed.set_footer(text=f"Include some text next time.\nEG: .qr bruh moment]")
            await ctx.send(embed=embed)

    @commands.command()
    async def animal(self, ctx):
        async with ctx.typing():
            soup = convertSoup('https://www.bestrandoms.com/random-animal-generator', headers2)
            animals = soup.findAll(class_='text-center')
            image = 'https://www.bestrandoms.com' + animals[2].find('img')['src']
            name = animals[2].find('img')['alt'].replace('logo', '')
            phrases = [f'A very swag {name}', f'The {name}', f'This {name} looks very epic', f'A fine looking {name}',
                       f'A very lovely {name}']
            desc = animals[4].text
            embed = discord.Embed(title=random.choice(phrases).replace('  ', ' '), color=discord.Color.random())
            embed.set_footer(text=desc)
            embed.set_image(url=image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(WebScraping(bot))
