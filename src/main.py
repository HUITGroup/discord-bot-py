import asyncio
import logging
import logging.config
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from api import start_web_server
from bot import bot
from db.database import init_models

ABS = Path(__file__).resolve().parents[1]
LOG = ABS / 'log'
LOG.mkdir(exist_ok=True)
load_dotenv(ABS / '.env')

TOKEN = os.getenv("DISCORD_TOKEN")
assert TOKEN is not None, '環境変数 DISCORD_TOKEN がセットされていません'

EXTENSIONS = [
  'bot.commands.help',
  'bot.commands.parrot',
  'bot.commands.member_year',
  'bot.events.member_join',
  'bot.events.timeline',
  'bot.events.grant_member_role',
  'tests.bot.commands.check_role'
]

with open(ABS / 'configs' / 'log_config.yaml') as f:
  log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)

async def main():
  await init_models()
  for cog in EXTENSIONS:
    await bot.load_extension(cog)
  await start_web_server()
  await bot.start(TOKEN)

if __name__ == '__main__':
  asyncio.run(main())
