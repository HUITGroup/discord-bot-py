from aiohttp import web
from aiohttp.web_request import Request
from pydantic import ValidationError

from api.schemas import RegisterRequest
from db import crud


async def handle_webhook(request: Request):
  try:
    raw_data = await request.json()
    data = RegisterRequest(**raw_data)
    print(data)
    await crud.pre_register_user(data.username, data.nickname, data.grade)
    return web.Response(text="ok")
  except ValidationError as e:
    return web.json_response({"error": str(e)}, status=400)
  except Exception as e:
    print(e)
    return web.json_response({"error": "Internal server error"}, status=500)

async def start_web_server():
  app = web.Application()
  app.router.add_post("/webhook/pre_register", handle_webhook)
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, "0.0.0.0", 8000)
  print('------------------------------------------------'*2)
  await site.start()
  print('server booted')
