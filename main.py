import os
import nextcord
from nextcord.ext import commands
import logging
logging.basicConfig(level=logging.WARNING)

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
    await log_all_past_messages()
    print(f"Ready, using {bot.user}")

async def log_message(message, guild_id):
    home_dir = os.path.expanduser("~")
    parliament_dir = os.path.join(home_dir, ".parliamentbomber")
    os.makedirs(parliament_dir, exist_ok=True)

    guild_dir = os.path.join(parliament_dir, f'guild_{guild_id}')
    os.makedirs(guild_dir, exist_ok=True)

    channel_name = message.channel.name.replace(' ', '_').lower()
    filename = os.path.join(guild_dir, f'{channel_name}.txt')
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f'{message.author.name}: {message.content}\n')

async def log_all_past_messages():
    tasks = []
    for guild in bot.guilds:
        for channel in guild.channels:
            if isinstance(channel, nextcord.TextChannel):
                async for message in channel.history(limit=None):
                    task = log_message(message, guild.id)
                    tasks.append(task)

@bot.event
async def on_message(message):
    guild = message.guild
    if guild:
        await log_message(message, guild.id)

    await bot.process_commands(message)

@bot.slash_command(description="My first slash command")
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")


bot.run("MTExMjUwNzA3MDA4MDYzMDgwNA.G_yAL0.YI-jpiY627RRfF8FtodNgTFUgrKa_MKYA2Ks-I")
