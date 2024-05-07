import os
import logging
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv


ABS = Path(__file__).resolve().parents[1]
load_dotenv(ABS / '.env')

TOKEN = os.getenv("DISCORD_TOKEN")

EXTENSIONS = ['cogs.member_year', 'cogs.timeline', 'cogs.member_join', 'cogs.help']

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

activity = discord.Activity(name="/help", type=discord.ActivityType.playing)

bot = commands.Bot('some_prefix', intents=intents, activity=activity)

@bot.event
async def on_ready():
  for cog in EXTENSIONS:
    await bot.load_extension(cog)

  await bot.tree.sync()

  print(f'Logged in as {bot.user.name}')

handler = logging.FileHandler(filename=ABS / 'log' / 'discord.log', encoding='utf-8', mode='w')

bot.run(TOKEN, log_handler=handler)
