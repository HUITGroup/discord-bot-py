import hashlib
import hmac
import json
import os
import re
import time
from datetime import datetime as dt
from datetime import timezone as tz
from pathlib import Path

import requests
from dotenv import load_dotenv

ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

HMAC_KEY_STR = os.getenv('HMAC_KEY')
assert HMAC_KEY_STR is not None

HMAC_KEY = HMAC_KEY_STR.encode()

# data = {
#   'username': 'sub8152'
# }

data = {
  'grade': 'b3',
  'username': 'sub8152',
  'nickname': 'misaizu_valid',
}

timestamp = dt.now(tz.utc).isoformat()
hmac_data = f'{json.dumps(data)}{timestamp}'.encode()

print(timestamp)

body = {
  'data': json.dumps(data),
  # 'signature': '',
  'signature': hmac.new(HMAC_KEY, hmac_data, hashlib.sha256).hexdigest(),
  'timestamp': timestamp,
  'year': 2025.0,
}

res = requests.post(
  # 'http://api.huitgroup.net:8000/submission',
  'http://localhost:8000/submission',
  json=body,
  headers={
    'Content-Type': 'application/json'
  },
)

# print(res.status_code)
print(res.json())
