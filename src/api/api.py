import hashlib
import hmac
import json
import logging
import os
import time
from collections.abc import Awaitable, Callable
from datetime import datetime as dt
from pathlib import Path
from typing import cast

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from dotenv import load_dotenv
from pydantic import ValidationError

from api.schemas.schema import BaseRequest, GrantRoleData, RegisterData
from bot import bot
from bot.events.grant_member_role import GrantMemberRole
from bot.events.member_join import MemberJoin
from db import crud
from utils.constants import GUILD_ID

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

HMAC_KEY_STR = os.getenv('HMAC_KEY')
if HMAC_KEY_STR is None:
  raise NotImplementedError(
    f'環境変数HMAC_KEYがセットされていません\n{HMAC_KEY_STR=}'
  )
HMAC_KEY = HMAC_KEY_STR.encode('utf-8')

ALLOWED_TIMESTAMP_DIFF = 300

logger = logging.getLogger('huitLogger')

def verify_signature(message: str, timestamp: str, signature: str) -> bool:
  try:
    data = f"{message}{timestamp}".encode()
    expected = hmac.new(HMAC_KEY, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
  except Exception:
    return False

async def submission(request: Request):
  logger.info('フォーム入力を検知しました')
  try:
    raw_data = await request.json()
    data = RegisterData(**json.loads(raw_data['data']))
    print(data)
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    logger.exception(e)
    return web.json_response({"error": "Internal server error"}, status=500)

  user, err = await crud.get_user_by_username(data.username)
  if err:
    logger.error('ユーザーの検索処理が異常終了しました')
    return web.json_response({"error": "internal server error"}, status=500)

  cog = bot.get_cog('MemberJoin')
  assert cog is not None
  cog = cast(MemberJoin, cog)

  if user is None:
    # nicknameが被っているかどうかの処理
    _, err = await crud.pre_register_user(
      data.username,
      data.nickname,
      data.grade
    )
    await cog.check_already_in_server(data.username)
  elif user.channel_id is None:
    # nicknameが被っているかどうかの処理
    _, err = await crud.pre_register_user(
      data.username,
      data.nickname,
      data.grade
    )
    await cog.check_already_in_server(data.username)
  else:
    # 学年更新処理のみ
    _, err = await crud.pre_register_user(
      data.username,
      data.nickname,
      data.grade
    )

  if err:
    logger.error('ユーザーの事前登録処理が異常終了しました')
    return web.json_response({"error": "internal server error"}, status=500)

  logger.info('フォーム入力処理を正常終了しました')

  return web.json_response({"ok": "accepted"}, status=200)

async def grant_member_role(request: Request):
  logger.info('チェック入れを検知しました')
  try:
    raw_data = await request.json()
    data = GrantRoleData(**json.loads(raw_data['data']))
    print(data)
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    logger.exception(e)
    return web.json_response({"error": "Internal server error"}, status=500)

  grant_cog = bot.get_cog('GrantMemberRole')
  assert grant_cog is not None
  member_join_cog = bot.get_cog('MemberJoin')
  grant_cog = cast(GrantMemberRole, grant_cog)
  member_join_cog = cast(MemberJoin, member_join_cog)

  found, err = await grant_cog.grant_member_role(data.username)

  if err:
    return web.json_response({"error": "Internal server error"}, status=500)
  if not found:
    logger.warning(f'`{data.username}` のユーザーが見つかりませんでした')
    return web.json_response({"error": "user is not found."}, status=404)

  err = await grant_cog.manage_channel(data.username)
  if err:
    return web.json_response({"error": "Internal server error"}, status=500)

  user, err = await crud.get_user_by_username(data.username)
  assert user is not None
  if err:
    logger.error('ユーザー検索処理が異常終了しました')
    return web.json_response({"error": "Internal server error"}, status=500)

  await member_join_cog.grant_grade_role(user.user_id, user.grade)

  logger.info('ロール付与処理を正常終了しました')
  return web.json_response({"ok": "accepted"}, status=200)

@web.middleware
async def hmac_auth_middleware(
  request: Request,
  handler: Callable[[web.Request], Awaitable[web.Response]]
) -> Response:
  """HMAC認証用ミドルウェア

  Args:
      request (Request): _description_
      handler (Callable[[web.Request], Awaitable[web.Response]]): _description_

  Raises:
      ValueError: _description_
      ValueError: _description_

  Returns:
      Response: _description_
  """
  try:
    raw_body = await request.json()
    body = BaseRequest(**raw_body)
    data = body.data
    timestamp = body.timestamp
    signature = body.signature
    year = body.year

    if abs(time.time() - dt.fromisoformat(timestamp).timestamp())\
      > ALLOWED_TIMESTAMP_DIFF:
      raise ValueError("Timestamp out of range")

    if not verify_signature(data, timestamp, signature):
      raise ValueError("Invalid signature")

  except ValidationError:
    # logger.warning('An unauthorized access has been detected')
    return web.json_response(
      {"error": "Unauthorized"},
      status=401,
    )
  except json.JSONDecodeError:
    # logger.warning('An unauthorized access has been detected')
    return web.json_response(
      {"error": "Unauthorized"},
      status=401
    )
  except Exception as e:
    # logger.exception(e)
    # logger.warning('An unauthorized access has been detected')
    return web.json_response(
      {"error": "Unauthorized"},
      status=401
    )

  db_year, err = await crud.get_member_role_year(GUILD_ID)
  if err:
    logger.error('member roleの年度検索処理が異常終了しました')

  if db_year is None:
    logger.critical(
      'member roleが紐付けられていません。' \
      '/link_member_roleコマンドで今年度のmember roleへの'\
      '紐付けを行ってください'
    )

  if year != db_year:
    return web.json_response(
      {
        "error": "The form you submitted has been outdated. "\
        f"The current version is {year}"
      },
      status=400
    )

  return await handler(request)

async def start_web_server():
  app = web.Application(middlewares=[hmac_auth_middleware])
  app.router.add_post("/submission", submission)
  app.router.add_post("/grant_member_role", grant_member_role)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", 8000)
  await site.start()
  logger.info('server booted')
