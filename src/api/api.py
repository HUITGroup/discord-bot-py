from aiohttp import web
from aiohttp.web_request import Request
from discord.ext import commands
from pydantic import ValidationError

from api.schemas import RegisterRequest
from bot import bot
from db import crud
from src.api.schemas.schema import GrantRoleRequest


async def pre_register(request: Request):
  try:
    raw_data = await request.json()
    data = RegisterRequest(**raw_data)
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
    data = GrantRoleRequest(**raw_data)
    print(data)

    cog = bot.get_cog('GrantMemberRole')
    assert cog is not None

    await cog.

  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

async def start_web_server():
  app = web.Application()
  app.router.add_post("/pre_register", pre_register)
  app.router.add_post("/grant_member_role", grant_member_role)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", 8000)
  print('------------------------------------------------'*2)
  await site.start()
  print('server booted')
