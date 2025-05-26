"""型定義部分"""
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar('T')

class BaseRequest(BaseModel, Generic[T]):
  data: T
  timestamp: str
  signature: str
  year: int

class RegisterData(BaseModel):
  grade: Literal['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'm1', 'm2', 'd', 'other']
  username: str
  nickname: str

class RegisterRequest(BaseRequest[RegisterData]):
  ...

class GrantRoleData(BaseModel):
  username: str

class GrantRoleRequest(BaseRequest[GrantRoleData]):
  ...
