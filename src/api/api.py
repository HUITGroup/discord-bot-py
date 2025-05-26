import hashlib
import hmac
import json
import os
import time
from datetime import datetime as dt
from pathlib import Path
from typing import Any

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from dotenv import load_dotenv
from pydantic import ValidationError

from api.schemas.schema import BaseRequest, GrantRoleData, RegisterData
from bot import bot
from db import crud
from utils.constants import GUILD_ID

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

HMAC_KEY_STR = os.getenv('HMAC_KEY')
if HMAC_KEY_STR is None:
  raise NotImplementedError()
HMAC_KEY = HMAC_KEY_STR.encode('utf-8')

ALLOWED_TIMESTAMP_DIFF = 300

def verify_signature(message: str, timestamp: str, signature: str) -> bool:
  try:
    data = f"{message}{timestamp}".encode()
    expected = hmac.new(HMAC_KEY, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
  except Exception:
    return False

async def submission(request: Request):
  try:
    raw_data = await request.json()
    data = RegisterData(**json.loads(raw_data['data']))
    print(data)
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

  user = await crud.get_user_by_username(data.username)
  cog = bot.get_cog('MemberJoin')
  assert cog is not None
  if user is None:
    # nicknameが被っているかどうかの処理
    await crud.pre_register_user(data.username, data.nickname, data.grade)
    await cog.check_already_in_server(data.username)
  elif user.channel_id is None:
    await crud.pre_register_user(data.username, data.nickname, data.grade)
    await cog.check_already_in_server(data.username)
  else:
    # 学年更新処理のみ
    await crud.pre_register_user(data.username, data.nickname, data.grade)

  return web.Response(text="ok")

async def grant_member_role(request: Request):
  try:
    raw_data = await request.json()
    data = GrantRoleData(**json.loads(raw_data['data']))
    print(data)
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

  cog = bot.get_cog('GrantMemberRole')
  assert cog is not None

  res = await cog.grant_member_role(data.username)

  if not res:
    return web.json_response({"error": "user is not found."}, status=404)

  res = await cog.manage_channel(data.username)

  return web.Response(text='ok')

@web.middleware
async def hmac_auth_middleware(request: Request, handler: web.RequestHandler) -> Response:
  try:
    raw_body = await request.json()
    body = BaseRequest(**raw_body)
    data = body.data
    timestamp = body.timestamp
    signature = body.signature
    year = body.year

    # timestampの妥当性チェック
    if abs(time.time() - dt.fromisoformat(timestamp).timestamp()) > ALLOWED_TIMESTAMP_DIFF:
      raise ValueError("Timestamp out of range")

    # HMAC署名チェック
    if not verify_signature(data, timestamp, signature):
      raise ValueError("Invalid signature")

  except Exception as e:
    return web.json_response({"error": "Unauthorized", "reason": str(e)}, status=401)

  db_year = await crud.get_year(GUILD_ID)
  assert db_year is not None

  if year != db_year:
    return web.json_response({"error": f"The form you submitted is outdated. The current version is {year}"}, status=400)

  return await handler(request)

async def start_web_server():
  app = web.Application(middlewares=[hmac_auth_middleware])
  app.router.add_post("/submission", submission)
  app.router.add_post("/grant_member_role", grant_member_role)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", 8000)
  print('------------------------------------------------'*2)
  await site.start()
  print('server booted')
