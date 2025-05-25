"""型定義部分"""
from pydantic import BaseModel


class RegisterData(BaseModel):
  grade: str
  username: str
  nickname: str

class RegisterRequest(BaseModel):
  data: RegisterData
  timestamp: str
  signature: str

class GrantRoleData(BaseModel):
  username: str

class GrantRoleRequest(BaseModel):
  data: GrantRoleData
  timestamp: str
  signature: str
