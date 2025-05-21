"""botインスタンス定義部分"""

import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

ABS = Path(__file__).resolve().parents[1]
load_dotenv(ABS / ".env")

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

activity = discord.Activity(name="/help", type=discord.ActivityType.playing)

bot = commands.Bot("some_prefix", intents=intents, activity=activity)

@bot.event
async def on_ready():  # noqa: D103
  synced = await bot.tree.sync()
  print(synced)

  print(f"Logged in as {bot.user.name}")
