from typing import Text
import discord

arrow = "<a:arrow:882812954314154045>"

class HelpEmbeds:
    
    def mainmenu():
        ilink = "https://discord.com/api/oauth2/authorize?client_id=889185777555210281&permissions=8&scope=bot%20applications.commands"
        embed = discord.Embed(title="Help Menu",
                             description=f"Invite the bot to your server [here]({ilink})\n"
                                         f"Join the support server [here](https://discord.gg/varietas)\n\n"
                                         "**Categories:**\n"
                                         f"{arrow} To view all command categories, click on the **dropdown menu below**!\n\n"
                                         "**Guide:**\n"
                                         f"{arrow} For command categories: Select a category below or do `v!help <category>`\n"
                                         f"{arrow} For help with specific commands: do `v!help <command>`\n\n"
                                         f"{arrow} If you run into any issues with any commands, feel free to join [the support server](https://discord.gg/varietas) for further assistance!",
                            colour=0x66bb6a)
        embed.set_footer(text="If the select menu disappears, it simply means the command has timed out. Run the command again to re-use the menu!")
        return embed
    
    def moderation():
        mod_commands = [["Ban", "Bans a member.\n`v!help ban`"], ["Kick", "Kicks a member.\n`v!help kick`"], ["Purge", "Purges a channel.\n`v!help purge`"], 
         ["Slowmode", "Puts a channel in slowmode.\n`v!help slowmode`"], ["Tempmute", "Tempmutes a member.\n`v!help tempmute`"], 
         ["Unban", "Unbans a member.\n`v!help unban`"]]
        embed = discord.Embed(title="Help Menu: Moderation", colour=0x66bb6a)
        for cmd in mod_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def news():
        def import_news():
            with open ("./info/news.txt", "r") as f:
                text = f.read()
                return text
        embed = discord.Embed(title="Help Menu: News", description=import_news(), colour=0x66bb6a)
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/bvk45myXtWIEDJEicf4KKvw4dbMtPMmAEWSx4MjWN10/%3Fwidth%3D676%26height%3D676/https/"
                                "media.discordapp.net/attachments/839256502820536340/889582730998849587/varietas_python_trans.png")
        return embed
        
    def miscellaneous():
        misc_commands = [["Reminder", "Make a reminder.\n`v!help reminder`"]]
        embed = discord.Embed(title="Help Menu: Miscellaneous", colour=0x66bb6a)
        for cmd in misc_commands:
                embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def utility():
        util_commands = [["Help", "Displays this help menu.\n`v!help`"], ["Invite", "Invite me to your server.\n`v!help invite`"], 
                         ["Ping", "Displays the bots latency.\n`v!help ping`"], ["Support", "Join the support server.\n`v!help support`"], 
                         ["Feedback", "Give feedback on the bot!\n`v!help feedback`"], ["Info", "Displays key info about the bot.\n`v!help info`"]]
        embed = discord.Embed(title="Help Menu: Utility", colour=0x66bb6a)
        for cmd in util_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def music():
        music_commands = [["Disconnect", "Disconnects the bot from the currently active vc.\n`v!help disconnect`"], ["Find", "Conducts a youtube search.\n`v!help find`"],
                          ["Lyrics", "Find lyrics for a song.\n`v!help lyrics`"], ["Now", "Displays currently playing song.\n`v!help now`"],
                          ["Pause", "Pause the currently playing song.\n`v!help pause`"], ["Play", "Add a song to the queue.\nv!help play"], 
                          ["Playlist", "Make your own playlist.\n`v!help playlist`"], ["Queue", "Display the bot's song queue\n`v!help queue`"], 
                          ["Remove", "Remove a song from the queue\n`v!help remove`"], ["Repeat", "Repeat the currently playing song\n`v!help repeat`"], 
                          ["Seek", "Seek through the currently playing song.\n`v!help seek`"], ["Shuffle", "Shuffle the current queue.\n`v!help shuffle`"], 
                          ["Skip", "Skip the currently playing song.\n`v!help skip`"], ["Stop", "Stop the queue.\n`v!help queue`"], 
                          ["Volume", "Adjust the volume for the currently playing song.\n`v!help volume`"]]
        embed = discord.Embed(title="Help Menu: Music", colour=0x66bb6a)
        for cmd in music_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def fun():
        fun_commands = [["Animal", "Sends a random animal.\n`v!help animal`"], ["Fact", "Sends a random fact.\n`v!help fact`"], ["Joke", "Sends a random joke.\n`v!help joke`"],
                        ["Roast", "Sends a random roast.\n`v!help roast`"], ["Weather", "Find out the weather for a specfic location.\n`v!help weather`"],
                        ["WPM", "Do a type speed test!\n`v!help wpm`"], ["WTP", "Who's that pokemon?\n`v!help wtp`"]]
        embed = discord.Embed(title="Help Menu: Fun", colour=0x66bb6a)
        for cmd in fun_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def economy():
        eco_commands = [["Economy commands", "Coming soon!"]]
        embed = discord.Embed(title="Help Menu: Economy", colour=0x66bb6a)
        for cmd in eco_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def configuration():
        conf_commands = [["Prefix", "Change the bots prefix.\n`v!help prefix`"]]
        embed = discord.Embed(title="Help Menu: Configuration", colour=0x66bb6a)
        for cmd in conf_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed
    
    def administration():
        admin_commands = [["Administration", "Probably wont keep this as admin is only for me and erase"]]
        embed = discord.Embed(title="Help Menu: Administration", colour=0x66bb6a)
        for cmd in admin_commands:
            embed.add_field(name=cmd[0], value=cmd[1], inline=True)
        return embed