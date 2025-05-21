"""型定義部分"""
from pydantic import BaseModel


class RegisterRequest(BaseModel):
  grade: str
  username: str
  nickname: str

class GrantRoleRequest(BaseModel):
  username: str
