"""型定義部分"""
from typing import Literal

from pydantic import BaseModel


class BaseRequest(BaseModel):
  data: str
  timestamp: str
  signature: str
  year: int

class RegisterData(BaseModel):
  grade: Literal['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd', 'other']
  username: str
  nickname: str

class GrantRoleData(BaseModel):
  username: str

