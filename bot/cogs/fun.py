import discord
from discord.ext import commands
import botconfig
import requests
import os
import asyncio
from typing import Union
from tools import embedbuilder as e
import random
import time
from bs4 import BeautifulSoup
import json

FONT = {'q': '𝗾', 'w': '𝘄', 'e': '𝗲', 'r': '𝗿', 't': '𝘁', 'y': '𝘆', 'u': '𝘂', 'i': '𝗶', 'o': '𝗼', 'p': '𝗽',
        'a': '𝗮', 's': '𝘀', 'd': '𝗱', 'f': '𝗳',
        'g': '𝗴', 'h': '𝗵', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'z': '𝘇', 'x': '𝘅', 'c': '𝗰', 'v': '𝘃', 'b': '𝗯',
        'n': '𝗻', 'm': '𝗺'}

HEADERS = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 "
                  "Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"
}

HEADERS2 = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, '
                          'like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53.'}

def convertSoup(link, user_agent=None):
    if user_agent is not None:
        return BeautifulSoup(requests.get(link, headers=user_agent, timeout=5).content, 'html.parser')
    page = requests.get(link, timeout=5)
    return BeautifulSoup(page.content, 'html.parser')

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
        if char in FONT:
            new += FONT[char]
        elif char.isupper() and char.lower() in FONT:
            new += FONT[char.lower()].upper()
        else:
            new += char
    return new

class Fun(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                {error.original}
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                retry after: {error.retry_after} seconds
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="An Unexpected Error Occurred!",
                description=f"""
                ```cmd
                {error.message}
                ```
                """,
                colour=0xef534e
            )
            await ctx.send(embed=embed)
        
    @commands.command(slash_command=True, description="whos that pokemon?")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def wtp(self, ctx):
        """You and you're friends get 3 tries to guess the right pokemon."""
        headers = {
            'Authorization': botconfig.DAGPI_TOKEN
        }
        res = requests.get('https://api.dagpi.xyz/data/wtp', headers=headers).json()
        
        file_q = res["question"]
        file_a = res["answer"]

        ctr = 0
        
        def check(m):
            return m.author.id != self.bot.user.id and m.channel.id == ctx.channel.id
        
        types = str([f"`{x}` " for x in res['Data']['Type']]).strip("']['")
        
        await ctx.send(embed=e.EmbedBuilder(self.bot).build_embed(
            title="Whos that pokemon?",
            description=f"Type(s): {types}",
            image=file_q
        ))
        
        while ctr <= 2:
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                
                if msg.content.lower() == res['Data']['name'].lower():
                    return await ctx.send(embed=e.EmbedBuilder(self.bot).build_embed(
                        title=f"{msg.author.name} got it right! The pokemon was {res['Data']['name']}.",
                        url=res['Data']['link'],
                        colour=0x66bb6a,
                        image=file_a
                    ))
                else:
                    ctr += 1
            except asyncio.TimeoutError:
                return await ctx.send(embed=e.EmbedBuilder(self.bot).build_embed(
                    title=f"No one answered in time! The pokemon was {res['Data']['name']}.",
                    url=res['Data']['link'],
                    colour=0xef534e,
                    image=file_a
                ))
        return await ctx.send(embed=e.EmbedBuilder(self.bot).build_embed(
            title=f"No one got it right! The pokemon was {res['Data']['name']}.",
            url=res['Data']['link'],
            colour=0xef534e,
            image=file_a
        ))
    
    @commands.command(slash_command=True, description="sends a joke")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def joke(self, ctx):
        """Send a joke"""
        headers = {
            'Authorization': botconfig.DAGPI_TOKEN
        }
        res = requests.get('https://api.dagpi.xyz/data/joke', headers=headers).json()
        
        await ctx.send(res["joke"])

    @commands.command(slash_command=True, description="sends a roast")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def roast(self, ctx):
        """Send a roast"""
        headers = {
            'Authorization': botconfig.DAGPI_TOKEN
        }
        res = requests.get('https://api.dagpi.xyz/data/roast', headers=headers).json()
        
        await ctx.send(res["roast"])
    
    @commands.command(slash_command=True, description="sends a fact")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def fact(self, ctx):
        """Send a fact"""
        headers = {
            'Authorization': botconfig.DAGPI_TOKEN
        }
        res = requests.get('https://api.dagpi.xyz/data/fact', headers=headers).json()
        
        await ctx.send(res["fact"])
        
    @commands.command(slash_command=True, alases=['forecast'], description="search for real-time weather, anywhere!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, query):
        """Search for real-time weather."""
        url = "https://community-open-weather-map.p.rapidapi.com/weather"

        querystring = {"q": query, "lat": "0", "lon": "0", "id": "2172797", "lang": "null",
                       "units": "\"metric\" or \"imperial\"", "mode": "xml, html"}
        h = {
            'x-rapidapi-key': "c97af16bb5msh4a9c4bd102924e7p13f694jsna81d3f25137a",
            'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
        }
        response = json.loads(requests.request("GET", url, headers=h, params=querystring).text)
        if response.get('message'):
            await ctx.send(embed=discord.Embed(description=f"No results found for `{query}`", color=0xff0000))
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
        
    @commands.command(slash_command=True, aliases=['typetest', 'wordsperminute'], description="play type-racer in discord!")
    async def wpm(self, ctx):
        """Repeat a given text as fast as you can to find your fastest WPM!"""
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        soup = convertSoup('https://www.bestrandoms.com/random-sentence', HEADERS)
        sentence = soup.find(class_='font-18').text
        embed = discord.Embed(description=convertFont(sentence), color=discord.Color.random())
        embed.set_author(name="Typing Test wpm", icon_url=ctx.author.avatar)
        embed.set_footer(text="Type in the sentence above as quick as possible")
        await ctx.send(embed=embed)
        await asyncio.sleep(0.5)
        begin = time.time()
        try:
            userInput = (await self.bot.wait_for('message', check=check, timeout=160)).content
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention} You took too long!")
        if userInput == convertFont(sentence):
            return await ctx.send("No copy pasting! >:(")
        if ' ' not in userInput:
            return await ctx.send("Keep practising! You can do better.")
        timeTaken = round(time.time() - begin, 2)
        sentence, userInput = sentence.lower(), userInput.lower()
        a = accuracy(sentence, userInput)
        userWords = len(userInput.split()) if ' ' in userInput else 1
        userLetters = len(userInput)
        await ctx.send(embed=discord.Embed(color=0xffff09,
                                           description=f"-You took **{timeTaken}** seconds with an accuracy of **{a}%**\n"
                                                       f"-About **{round((60 / timeTaken) * userWords, 1)}** words per minute\n"
                                                       f"-Or **{round(userLetters / timeTaken, 3)}** Letters per second"))
        
    @commands.command(slash_command=True, description="sends you an animal picture")
    async def animal(self, ctx):
        """Send an animal picture"""
        async with ctx.typing():
            soup = convertSoup('https://www.bestrandoms.com/random-animal-generator', HEADERS2)
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
    

def setup(bot:commands.Bot):
    bot.add_cog(Fun(bot))
