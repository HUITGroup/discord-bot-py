# discord-bot-py
## 開発環境について
このプロジェクトでは uv と ruff を導入しています。

### uv 導入方法

#### 1. インストール
Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

MacOS
```bash
brew install uv
```

#### 2. 環境構築
```bash
uv python install 3.11
uv sync
```

### ruff 導入方法

#### 1. ruffをグローバルにインストール
```bash
uv tool install ruff
```

#### 2. ruff拡張機能のインストール
VSCodeで[Ruffの拡張機能](https://marketplace.visualstudio.com/items/?itemName=charliermarsh.ruff)をインストールします

## .envについて
`discord-bot-py`直下に`.env`を作成して、環境変数を定義しておいてください。テンプレートを置いておきます。
```
DISCORD_TOKEN=
GUILD_ID=543343653394055169
BOT_ROLE_ID=1235844994372341783
GUEST_ROLE_ID=821021445006163978
WELCOME_CHANNEL_ID=781880127579619401
INFO_CHANNEL_ID=864696712115519489
TIMES_MESSAGE_ID=862023717134794832

MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_USER=huit_dc
MYSQL_PASSWORD=huit_dc
MYSQL_DATABASE=huit_dc
MYSQL_ADDRESS=localhost
MYSQL_PORT=3306
```

`DISCORD_TOKEN`については自分のdiscord botのトークンを使うかmisaizuにお問い合わせください

## DBについて
`sqlalchemy`を使っているので一応MySQLでもPostgreSQLでもSQLiteでも動きます。但しMySQL以外を使う場合は`docker-compose.yaml`と`src/db/database.py`辺りの書き換えが必要なので注意してください

## デプロイについて
`0.0.0.0/0`の8000番ポートを空ける必要があるので注意してください

