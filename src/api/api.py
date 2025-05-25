import hashlib
import hmac
import os
import time
from pathlib import Path

from aiohttp import web
from aiohttp.web_request import Request
from discord.ext import commands
from dotenv import load_dotenv
from pydantic import ValidationError

from api.schemas import RegisterRequest
from bot import bot
from db import crud
from src.api.schemas.schema import GrantRoleRequest

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

HMAC_KEY = os.getenv('HMAC_KEY')

ALLOWED_TIMESTAMP_DIFF = 300

def verify_signature(message: str, timestamp: str, signature: str) -> bool:
  try:
    data = f"{message}{timestamp}".encode()
    expected = hmac.new(HMAC_KEY, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
  except Exception:
    return False

async def pre_register(request: Request):
  try:
    raw_data = await request.json()
    data = RegisterRequest(**raw_data).data
    print(data)
    assert data.grade in {'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd', 'other'}

    await crud.pre_register_user(data.username, data.nickname, data.grade)
    return web.Response(text="ok")
  except (ValidationError, AssertionError) as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

async def grant_member_role(request: Request):
  try:
    raw_data = await request.json()
    data = GrantRoleRequest(**raw_data).data
    print(data)

    cog = bot.get_cog('GrantMemberRole')
    assert cog is not None

    res = await cog.grant_member_role(data.username)

    if res:
      return web.Response(text="ok")
    else:
      return web.json_response({"error": "user is not found."}, status=404)
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

@web.middleware
async def hmac_auth_middleware(request: Request, handler):
  try:
    body: dict[str, str] = await request.json()
    data = body.get("data")
    timestamp = body.get("timestamp")
    signature = body.get("signature")

    # 1. 値がすべて揃っているか
    if not all([data, timestamp, signature]):
      raise ValueError("Missing fields")

    # 2. timestampの妥当性チェック
    if abs(time.time() - int(timestamp)) > ALLOWED_TIMESTAMP_DIFF:
      raise ValueError("Timestamp out of range")

    # 3. HMAC署名チェック
    if not verify_signature(data, timestamp, signature):
      raise ValueError("Invalid signature")

  except Exception as e:
    return web.json_response({"error": "Unauthorized", "reason": str(e)}, status=401)

  return await handler(request)

async def start_web_server():
  app = web.Application(middlewares=[hmac_auth_middleware])
  app.router.add_post("/pre_register", pre_register)
  app.router.add_post("/grant_member_role", grant_member_role)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", 8000)
  print('------------------------------------------------'*2)
  await site.start()
  print('server booted')
