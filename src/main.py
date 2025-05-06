import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from api import start_web_server
from bot import bot
from db.database import init_models

ABS = Path(__file__).resolve().parents[1]
LOG = ABS / 'log'
LOG.mkdir(exist_ok=True)
load_dotenv(ABS / '.env')

TOKEN = os.getenv("DISCORD_TOKEN")

log_handler = logging.FileHandler(filename=LOG / 'discord.log', encoding='utf-8', mode='w')
log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

async def main():
  await init_models()
  await start_web_server()
  await bot.start(TOKEN)

if __name__ == '__main__':
  asyncio.run(main())

