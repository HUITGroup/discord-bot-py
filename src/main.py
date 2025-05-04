import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers.router import router
from src.bot import bot

ABS = Path(__file__).resolve().parents[1]
LOG = ABS / 'log'
LOG.mkdir(exist_ok=True)
load_dotenv(ABS / '.env')

TOKEN = os.getenv("DISCORD_TOKEN")

log_handler = logging.FileHandler(filename=LOG / 'discord.log', encoding='utf-8', mode='w')


@asynccontextmanager
async def lifespan(app: FastAPI):
  asyncio.create_task(bot.run(TOKEN, log_handler=log_handler))
  yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)

@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
  print(exc)
  return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
