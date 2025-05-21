import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com.feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./huit-bot-105deb6489c9.json')

client = gspread.authorize(creds)

spreadsheet = client.open('2025年度 北大 IT 研究会 入会フォーム（回答）')

worksheet = spreadsheet.sheet1
d = worksheet.get_all_records()

for l in d:
  print(l)
