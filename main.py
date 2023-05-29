import os
import nextcord
from nextcord.ext import commands
import logging
from dotenv import load_dotenv
import asyncio

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


@bot.event
async def on_ready():
    print(f"Ready, using {bot.user}")


async def log_message(message, guild_id):
    guild_dir = os.path.join(parliament_dir, f'guild_{guild_id}')
    os.makedirs(guild_dir, exist_ok=True)

    channel_name = message.channel.name.replace(' ', '_').lower()
    filename = os.path.join(guild_dir, f'{channel_name}.txt')

    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f'{message.author.name}: {message.content}\n')


async def log_all_past_messages():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            guild_dir = os.path.join(parliament_dir, f'guild_{guild.id}')
            os.makedirs(guild_dir, exist_ok=True)

            async for message in channel.history(limit=None):
                await log_message(message, guild.id)


@bot.event
async def on_message(message):
    guild = message.guild
    if guild:
        await log_message(message, guild.id)

    await bot.process_commands(message)


@bot.slash_command(description="Log all past messages")
async def log_past_messages(interaction: nextcord.Interaction):
    await interaction.send("Logging all past messages...")
    await log_all_past_messages()


@bot.slash_command(description="Initialize logger")
async def init_logger(interaction: nextcord.Interaction):
    await interaction.send("Logger initialized.")


token = os.environ.get("TOKEN")
bot.run(token)