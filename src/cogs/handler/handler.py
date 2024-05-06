import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime as dt, date

import psycopg2
from dotenv import load_dotenv


ABS = Path(__file__).resolve().parents[2]
load_dotenv(ABS / '.env')

POSTGRES_ROOT_PASSWORD = os.getenv("POSTGRES_ROOT_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_ADDRESS = os.getenv("POSTGRES_ADDRESS")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

class Handler:
  def __init__(self) -> None:
    while True:
      try:
        self.conn = psycopg2.connect(host=POSTGRES_ADDRESS, dbname=POSTGRES_DATABASE, user=POSTGRES_USER, password=POSTGRES_PASSWORD)

        break
      except psycopg2.OperationalError as e:
        print("SQL Connection Error")
        print(e)
        time.sleep(10)

    schema1 = (
      "CREATE TABLE IF NOT EXISTS timeline_channel (" \
      "        guild_id    BIGINT CHECK(guild_id >= 0) NOT NULL PRIMARY KEY," \
      "        timeline_id BIGINT CHECK(timeline_id >= 0) NOT NULL" \
      ");"
    )

    schema2 = (
      "CREATE TABLE IF NOT EXISTS timeline_message (" \
      "        timeline_message_id BIGINT CHECK(timeline_message_id >= 0) NOT NULL PRIMARY KEY," \
      "        original_message_id BIGINT CHECK(original_message_id >= 0) NOT NULL"\
      ");"
    )

    schema3 = (
      "CREATE TABLE IF NOT EXISTS user_deadlines (" \
      "        user_id BIGINT CHECK(user_id >= 0) NOT NULL PRIMARY KEY," \
      "        deadline DATE NOT NULL" \
      ");"
    )

    for schema in [schema1, schema2, schema3]:
      with self.conn.cursor() as cur:
        cur.execute(schema)

  def get_timeline_channel_id(self, guild_id: int) -> Optional[int]:
    with self.conn.cursor() as cur:
      cur.execute('SELECT timeline_id FROM timeline_channel WHERE guild_id = %s', (guild_id, ))
      timeline_channel_id = cur.fetchone()

    timeline_channel_id = timeline_channel_id[0] if timeline_channel_id else None
    return timeline_channel_id

  def get_timeline_message_id(self, original_message_id: int) -> Optional[int]:
    with self.conn.cursor() as cur:
      cur.execute('SELECT timeline_message_id FROM timeline_message WHERE original_message_id = %s', (original_message_id, ))
      timeline_message_id = cur.fetchone()

    timeline_message_id = timeline_message_id[0] if timeline_message_id else None
    return timeline_message_id

  def del_timeline(self, original_message_id: int) -> None:
    with self.conn.cursor() as cur:
      cur.execute('DELETE FROM timeline_message WHERE original_message_id = %s', (original_message_id, ))
      self.conn.commit()

    return

  def register_timeline_channel(self, guild_id: int, channel_id: int) -> None:
    with self.conn.cursor() as cur:
      cur.execute('INSERT INTO timeline_channel(guild_id, timeline_id) VALUES(%s, %s) ON CONFLICT (guild_id) DO UPDATE SET timeline_id = %s', (guild_id, channel_id, channel_id))
      self.conn.commit()

  def register_message(self, timeline_message_id: int, original_message_id: int) -> None:
    with self.conn.cursor() as cur:
      cur.execute('INSERT INTO timeline_message(timeline_message_id, original_message_id) VALUES(%s, %s)', (timeline_message_id, original_message_id))
      self.conn.commit()

  def get_users_by_deadline(self, deadline: date) -> Optional[list[int]]:
    with self.conn.cursor() as cur:
      cur.execute('SELECT user_id FROM user_deadlines WHERE deadline = %s', (deadline, ))
      user_ids = cur.fetchall()

    user_ids = [i[0] for i in user_ids]
    return user_ids

  def register_user(self, user_id: int, deadline: date) -> None:
    with self.conn.cursor() as cur:
      try:
        cur.execute('INSERT INTO user_deadlines(user_id, deadline) VALUES(%s, %s)', (user_id, deadline))
        self.conn.commit()
      except Exception as e:
        print(e)

  def delete_user(self, user_id: int) -> None:
    with self.conn.cursor() as cur:
      cur.execute('DELETE FROM user_deadlines WHERE user_id = %s', (user_id, ))
      self.conn.commit()

handler = Handler()
