"""botインスタンス定義部分"""

import asyncio
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api import start_web_server

ABS = Path(__file__).resolve().parents[1]
load_dotenv(ABS / ".env")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

EXTENSIONS = [
  # "src..member_year",
  # "cogs.timeline",
  # "cogs.member_join",
  # "cogs.help",
  # "cogs.parrot",
  # "cogs.check_permissions",
  'bot.commands.help',
  'bot.commands.parrot',
  'bot.commands.member_year',
  'bot.events.member_join',
  'bot.events.timeline',
  'tests.bot.commands.check_role'
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

activity = discord.Activity(name="/help", type=discord.ActivityType.playing)

bot = commands.Bot("some_prefix", intents=intents, activity=activity)

@bot.event
async def on_ready():  # noqa: D103
  for cog in EXTENSIONS:
    await bot.load_extension(cog)

  synced = await bot.tree.sync()
  print(synced)

  print(f"Logged in as {bot.user.name}")
