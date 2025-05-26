import hashlib
import hmac
import os
import re
import time
from datetime import datetime as dt
from pathlib import Path

import requests
from dotenv import load_dotenv

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

HMAC_KEY_STR = os.getenv('HMAC_KEY')
assert HMAC_KEY_STR is not None

HMAC_KEY = HMAC_KEY_STR.encode()

data = {
  'username': 'sub8152'
}

# data = {
#   'grade': 'b3',
#   'username': 'sub8152',
#   'nickname': 'misaizu_valid',
# }

timestamp = dt.now().isoformat()
hmac_data = f'{data}{timestamp}'.encode()

body = {
  'data': data,
  'signature': hmac.new(HMAC_KEY, hmac_data, hashlib.sha256).hexdigest(),
  'timestamp': timestamp,
  'year': 2025,
}

res = requests.post(
  'http://localhost:8000/grant_member_role',
  json=body,
  headers={
    'Content-Type': 'application/json'
  },
)

print(res.status_code)
# print(res.json())
