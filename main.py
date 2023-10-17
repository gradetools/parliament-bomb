import os
import logging
import subprocess
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import json
from time import sleep
load_dotenv()
logging.basicConfig(level=logging.WARNING)
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)
logger = logging.getLogger('nextcord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def load_json_to_dict(nix_file_path):
        output = subprocess.check_output(['nix-instantiate', '--eval', '--json', "--verbose" , "--strict" , nix_file_path])
        output = json.loads(output)
        return output

def format_json(input_json):
        json_output = json.loads(input_json)
        formatted_output = json.dumps(json_output, indent=4)
        return formatted_output
    
@bot.event # ready sequence duh
async def on_ready():
    print(f"Ready, using {bot.user}")

nameofserver = load_json_to_dict("server.nix")
# class Server:
#     def __init__(self):
#         self.name = nameofserver["serverName"]
#         self.channels = nameofserver["channels"]
#     def name(self):
#         return self.name
#     def channels(self):
#         return self.channels
    
    
# pbts = Server()
# pbts.channels()
@bot.slash_command(description="rebuild")
async def rebuild(interaction: nextcord.Interaction):
    # status = "rebuilding"
    # ctx = await interaction.send(status)
    # statuses = ["rebuilding", "rebuilding.", "rebuilding..", "rebuilding..."]
    # for i in range(3):
    #     for status in statuses:
    #         await ctx.edit(status)
    #         sleep(0.1)
    # await ctx.edit("rebuild complete")

    # guild = interaction.guild
    # nameeval = load_json_to_dict("server.nix")
    # for name in nameeval:
    #     print(name)
    # #nametochange = nameeval["serverName"]
    # # print(nametochange)
    # interaction.response(pbts.printname)
    pass
last_user = None

@bot.slash_command(description="alexping")
@commands.cooldown(5, 10, commands.BucketType.user)

async def alex(interaction:nextcord.Interaction):
    global last_user
    if last_user == interaction.user:
        await interaction.send("stop spamming you donut", ephemeral=True)
    else:
        last_user = interaction.user
        print(f"last_user: {last_user}")
        await interaction.send("trolling alex", ephemeral=True)
        await interaction.channel.send("<@546022174734155796>")
        with open('commandlog.json', 'w') as f:
            json.dump({'last_user(ran alex command)': str(last_user)}, f)
token = os.environ.get("TOKEN")
bot.run(token)
