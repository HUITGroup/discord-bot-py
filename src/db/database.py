"""DB接続設定部分"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
  async_sessionmaker,
  create_async_engine,
)
from sqlalchemy.orm import declarative_base

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / ".env")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_ADDRESS = os.getenv("MYSQL_ADDRESS")
MYSQL_PORT = os.getenv("MYSQL_PORT")

assert all([
  MYSQL_USER,
  MYSQL_PASSWORD,
  MYSQL_ADDRESS,
  MYSQL_PORT,
  MYSQL_DATABASE
  ]), f'MySQL関連の環境変数がNoneです\n{MYSQL_USER=}\n{MYSQL_PASSWORD=}\n{MYSQL_DATABASE=}\n{MYSQL_ADDRESS=}\n{MYSQL_PORT=}\n'

DATABASE_URL = (
  f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}"
  f"@{MYSQL_ADDRESS}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def init_models() -> None:
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
