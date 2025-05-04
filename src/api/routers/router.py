"""router定義部分"""

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.schemas.schema import RegisterRequest
from src.db.crud import pre_register_user

router = APIRouter(prefix='/api')

@router.post(path='/pre_register')
async def pre_register(req: RegisterRequest):
  res = pre_register_user(req.username, req.nickname, req.grade)
  if res:
    return JSONResponse(content={})
  else:
    return JSONResponse(content={
      'detail': 'internal server error'
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
