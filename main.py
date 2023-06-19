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
                        'mentions': [mention.name for mention in message.mentions]
                    }
                    file.write(json.dumps(data, indent=4))
                    file.write("\n")


@bot.slash_command(description="Log all past messages")
async def log_past_messages(interaction: nextcord.Interaction):
    await interaction.send("Logging all past messages...")
    await log_all_past_messages()

@bot.slash_command(description="getunixtime")
async def get_unix_time(interaction: nextcord.Interaction):
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
