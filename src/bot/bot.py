"""botインスタンス定義部分"""

import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

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
  'src.bot.commands.help',
  'src.bot.commands.parrot',
  'src.bot.events.member_join',
  'src.bot.events.timeline',
  'src.tests.bot.commands.check_role'
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
