import os
import json
import asyncio
import logging
import requests
import nextcord
import subprocess
import psutil
import datetime
from nextcord.ext import commands
from nextcord import Embed
from dotenv import load_dotenv
from uptime import uptime



load_dotenv()
logging.basicConfig(level=logging.WARNING)

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

home_dir = os.path.expanduser("~")
parliament_dir = os.path.join(home_dir, ".parliamentbomber")
os.makedirs(parliament_dir, exist_ok=True)

@bot.event # ready sequence duh
async def on_ready():
    print(f"Ready, using {bot.user}")
    
async def log_all_past_messages(): # switched to a daily refresh model
    for guild in bot.guilds:
        guild_dir = os.path.join(parliament_dir, f'guild_{guild.name}')
        os.makedirs(guild_dir, exist_ok=True)

        for channel in guild.text_channels:
            channel_name = channel.name.replace(' ', '_').lower()
            filename = os.path.join(guild_dir, f'{channel_name}.json')

            with open(filename, 'a', encoding='utf-8') as file:
                messages = [] 
                
                async for message in channel.history(limit=None):
                    data = {
                        'author': message.author.name,
                        'content': message.content,
                        'message_id': message.id,
                        'author_id': message.author.id,
                        'channel': str(message.channel),
                        'channel_id': message.channel.id,
                        'mentions': [mention.name for mention in message.mentions],
                        'timestamp': int(message.created_at.timestamp())
                    }
                    messages.append(data) 

                file.write(json.dumps({"messages": messages}, indent=4))
                file.write("\n")




async def log_all_past_messages_continuous(): # switched to a daily refresh model
    for guild in bot.guilds:
        filename = os.path.join(parliament_dir, 'SYS_CONTINUOUS.json')
        guild_dir = os.path.join(parliament_dir, f'guild_{guild.name}')
        os.makedirs(guild_dir, exist_ok=True)
        for channel in guild.text_channels:
            filename = os.path.join(guild_dir + filename)

            with open(filename, 'a', encoding='utf-8') as file:
                messages = [] 
                
                async for message in channel.history(limit=None):
                    data = {
                        'author': message.author.name,
                        'content': message.content,
                        'message_id': message.id,
                        'author_id': message.author.id,
                        'channel': str(message.channel),
                        'channel_id': message.channel.id,
                        'mentions': [mention.name for mention in message.mentions],
                        'timestamp': int(message.created_at.timestamp())
                    }
                    messages.append(data) 

                file.write(json.dumps({"messages": messages}, indent=4))
                file.write("\n")


@bot.slash_command(description="Log all past messages")
async def log_past_messages(interaction: nextcord.Interaction):
    await interaction.send("Logging all past messages...")
    await log_all_past_messages()


@bot.slash_command(description="Continuously Fetch to SYS.CONTINOUS.json (no channel seperating)")
async def continuous_fetch(interaction: nextcord.Interaction):
    json_data = """
    {
        "content": "",
        "tts": false,
        "embeds": [
            {
                "id": 404236386,
                "description": "Your request to `log_all_past_messages_continous`\\nwas sent successfully! You should see your output in your\\n$parliamentdir/$guild_dir/SYS_CONTINOUS.json\\n\\n**What's this for?**\\nGathering ALL data from ALL channels for advanced\\nparsing with tools like matplotlib. All data is timestamped\\nand marked with their channel ID and name. \\n\\n**Details:**\\nworkdir: $parliament_dir/$guild_dir/SYS_CONTINOUS.json\\nLogging: All Channels\\nContinous: True\\n\\n**Not Working?**\\nTry reloading main.py, or call a Developer.",
                "fields": [],
                "author": {
                    "name": "parliamentbomb_experimental | system message"
                },
                "thumbnail": {
                    "url": "https://em-content.zobj.net/source/twitter/376/check-mark-button_2705.png"
                },
                "title": "Request Sent!",
                "footer": {
                    "text": "parliamentbomb-experimental | running within nix-shell | unix_millis"
                },
                "color": 7844436
            }
        ],
        "components": [],
        "actions": {}
    }
    """
    parsed_data = json.loads(json_data)
    for embed_dict in parsed_data['embeds']:
        embed = Embed.from_dict(embed_dict)
        await interaction.response.send_message(embed=embed)
    await log_all_past_messages_continuous()


def get_directory_size(directory):
    total_size = 0
    for path, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    return total_size


@bot.slash_command(description="Display system information")
async def sysinfo(interaction: nextcord.Interaction):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    kernel = os.uname()
    uptime_seconds = uptime()
    in_nix_shell = os.environ.get('IN_NIX_SHELL') is not None
    uptime_hours = uptime_seconds / 3600
    parliamentd_status = os.environ.get('parliamentd_status') is not None
    directory_size = get_directory_size(os.path.expanduser('~/.parliamentbomber'))
    embed = Embed(title="Host System Information", color=0x00ff00)
    embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=False)
    embed.add_field(name="Memory Usage", value=f"{memory}%", inline=False)
    embed.add_field(name="Disk Usage", value=f"{disk}%", inline=False)
    embed.add_field(name="Kernel Version", value=kernel, inline=False)
    embed.add_field(name="Uptime", value=f"{uptime_hours} hours", inline=False)
    embed.add_field(name="Running in Nix-Shell?", value=str(in_nix_shell), inline=False)
    embed.add_field(name="parliamentd Status", value=parliamentd_status, inline=False)
    embed.add_field(name="Log Size", value=f"{directory_size} bytes", inline=False)
    embed.set_thumbnail(url='https://em-content.zobj.net/source/twitter/376/information_2139-fe0f.png')
    await interaction.response.send_message(embed=embed)


@bot.slash_command(description="getunixtime")
async def get_unix_time(interaction: nextcord.Interaction):
    unixtime = requests.get("https://worldtimeapi.org/api/timezone/America/Edmonton")
    unixtimeformat = unixtime.json()
    unixtime_value = unixtimeformat["unixtime"]
    await interaction.send(f"time: {unixtime_value}")

#@bot.slash_command(description="unixtime_again")
#async def unixtime_again(interaction: nextcord.Interaction):
#    unixtime = requests.get("https://worldtimeapi.org/api/timezone/America/Edmonton")
#    unixtimeformat = unixtime.json()
#    unixtime_value = unixtimeformat["unixtime"]
#    await interaction.send(f"time: {unixtime_value}")

@bot.slash_command(description="about parliamentbomb")
async def about(interaction: nextcord.Interaction):
    embed = Embed(title="About Parliamentbomb", color=0x00ff00)
    embed.add_field(name="Synopsis", value=f"Parliament Bomb is a Discord Bot that doesn't sacrifice on it's looks.", inline=False)
    embed.add_field(name="Version", value=f"rolling", inline=False)
    embed.add_field(name="Git", value=f"https://github.com/gradetools/parliament-bomb", inline=False)
    embed.set_thumbnail(url='https://em-content.zobj.net/source/twitter/376/bomb_1f4a3.png')
    await interaction.response.send_message(embed=embed)


@bot.slash_command(guild_ids=[1112507308661030992])
async def summary(interaction: nextcord.Interaction, password: str):
    if password != "balls123":
        await interaction.send("no wrong lol")

@bot.event
async def on_presence_update(before, after):
    rtlStatusChannel = bot.get_channel(1201528490722328668)
    avatar_url = str(after.avatar.url)
    if before.status != after.status:
        if after.status == 'dnd':
            color = 0xFF0000 
        elif after.status == 'online':
            color = 0x00FF00 
        elif after.status == 'idle':
            color = 0xFFFF00 
        else: 
            color = 0x808080 

        embed = Embed(title="Status Update!", color=color)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Username", value=after.name, inline=True)
        embed.add_field(name="User ID", value=str(after.id), inline=True)
        embed.add_field(name="Status Change", value=f"{before.status if before.status else 'n/a'} -> {after.status if after.status else 'n/a'}", inline=True)
        timestamp = int(datetime.datetime.utcnow().timestamp() * 1000)
        embed.set_footer(text=f"Unix Timestamp: {timestamp}")
        await rtlStatusChannel.send(embed=embed)

    if len(before.activities) > len(after.activities):
        action = "stopped"
    elif len(before.activities) < len(after.activities):
        action = "started"
    else:
        return

    if set(before.activities) != set(after.activities):
        rtlActivityChannel = bot.get_channel(1201663950928744458)
        embed = Embed(title="User Presence Update!", color=0x00ff00)
        embed.add_field(name="Username", value=after.name, inline=True)
        embed.add_field(name="User ID", value=str(after.id), inline=True)
        embed.add_field(name="Status:", value=action, inline=False)

        for activity in after.activities:
            if isinstance(activity, nextcord.Game):
                embed.add_field(name="Game Title", value=activity.name, inline=False)
                embed.add_field(name="Currently Playing", value=activity.details, inline=False)
                embed.add_field(name="Action String", value=activity.state, inline=False)
                embed.set_thumbnail(url=activity.large_image_url)
            elif isinstance(activity, nextcord.Streaming):
                embed.add_field(name="Streaming", value=activity.name, inline=False)
            elif isinstance(activity, nextcord.Spotify):
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Song", value=activity.title, inline=False)
                embed.add_field(name="Album", value=activity.album, inline=False)
                embed.add_field(name="Artist", value=activity.artist, inline=False)
            elif isinstance(activity, nextcord.Activity):
                embed.add_field(name="Watching", value=activity.name, inline=False)
                
        timestamp = int(datetime.datetime.utcnow().timestamp() * 1000)
        embed.set_footer(text=f"Unix Timestamp: {timestamp}")
        await rtlActivityChannel.send(embed=embed)



@bot.event
async def on_message_delete(message):
    log_channel = bot.get_channel(1201696387671265321)

    duration = int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()) - int(message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp())

    embed = nextcord.Embed(title="Message Deleted", color=nextcord.Color.red())
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name="Author", value=message.author.name, inline=False)
    embed.add_field(name="Author ID", value=message.author.id, inline=False)
    embed.add_field(name="Deleted Message ID", value=message.id, inline=False)    
    embed.add_field(name="Content (at time of deletion)", value=message.content, inline=False)
    embed.add_field(name="Written At", value=int(message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()), inline=True)
    embed.add_field(name="Deleted At", value=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()), inline=True)
    embed.add_field(name="Duration Available (seconds)", value=str(duration), inline=True)
    embed.add_field(name="Channel", value=message.channel.name, inline=True)
    embed.set_footer(text=f"All timestamps are in Unix Time")

    await log_channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    log_channel = bot.get_channel(1201698699248410684)

    embed = nextcord.Embed(title="Message Edited", color=nextcord.Color.blue())
    embed.set_thumbnail(url=after.author.avatar.url)
    embed.add_field(name="Author", value=after.author.name, inline=False)
    embed.add_field(name="Author ID", value=after.author.id, inline=False)
    embed.add_field(name="Message ID", value=after.id, inline=False)
    embed.add_field(name="Original Content", value=before.content, inline=False)
    embed.add_field(name="Edited Content", value=after.content, inline=False)
    embed.add_field(name="Written At", value=int(before.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()), inline=True)
    embed.add_field(name="Edited At", value=int(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()), inline=True)
    embed.add_field(name="Channel", value=after.channel.name, inline=True)
    embed.set_footer(text=f"All timestamps are in Unix Time")

    await log_channel.send(embed=embed)
    
token = os.environ.get("TOKEN")
bot.run(token)

