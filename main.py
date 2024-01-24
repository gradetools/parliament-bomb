import os
import json
import asyncio
import logging
import requests
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
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
                async for message in channel.history(limit=None):
                    data = {
                        'author': message.author.name,
                        'content': message.content,
                        'message_id': message.id,
                        'author_id': message.author.id,
                        'channel': str(message.channel),
                        'mentions': [mention.name for mention in message.mentions],
                        'timestamp': int(message.created_at.timestamp()) # Convert datetime to Unix timestamp
                    }
                    file.write(json.dumps(data, indent=4))
                    file.write("\n")


async def log_all_past_messages_continuous(): # switched to a daily refresh model
    for guild in bot.guilds:
        filename = os.path.join(parliament_dir, 'SYS_CONTINUOUS.json')
        guild_dir = os.path.join(parliament_dir, f'guild_{guild.name}')
        os.makedirs(guild_dir, exist_ok=True)


    with open(filename, 'a', encoding='utf-8') as file:
        for guild in bot.guilds:
            for channel in guild.text_channels:
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
                    file.write(json.dumps(data, indent=4))
                    file.write("\n")


@bot.slash_command(description="Log all past messages")
async def log_past_messages(interaction: nextcord.Interaction):
    await interaction.send("Logging all past messages...")
    await log_all_past_messages()

import json
from nextcord import Embed

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


@bot.slash_command(description="getunixtime")
async def get_unix_time(interaction: nextcord.Interaction):
    unixtime = requests.get("https://worldtimeapi.org/api/timezone/America/Edmonton")
    unixtimeformat = unixtime.json()
    unixtime_value = unixtimeformat["unixtime"]
    await interaction.send(f"time: {unixtime_value}")

@bot.slash_command(description="unixtime_again")
async def unixtime_again(interaction: nextcord.Interaction):
    unixtime = requests.get("https://worldtimeapi.org/api/timezone/America/Edmonton")
    unixtimeformat = unixtime.json()
    unixtime_value = unixtimeformat["unixtime"]
    await interaction.send(f"time: {unixtime_value}")


@bot.slash_command(guild_ids=[1112507308661030992])
async def summary(interaction: nextcord.Interaction, password: str):
    if password != "balls123":
        await interaction.send("no wrong lol")

token = os.environ.get("TOKEN")
bot.run(token)

