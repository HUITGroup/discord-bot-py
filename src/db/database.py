"""DB接続設定部分"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)
from sqlalchemy.orm import declarative_base

ABS = Path(__file__).resolve().parents[1]
load_dotenv(ABS / ".env")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_ADDRESS = os.getenv("POSTGRES_ADDRESS")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = (
  f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
  f"@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()
