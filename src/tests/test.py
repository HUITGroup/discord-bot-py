import requests


res = requests.post('http://0.0.0.0:8000/webhook/pre_register',
  json={
    "username": "sub8152",
    "nickname": "misaizu_valid",
    "grade": "b4",
  },
  headers={
    "Content-Type": "application/json"
  }
)
print(res.status_code)
