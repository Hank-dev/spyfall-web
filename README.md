# Spyfall Web

Single-port Spyfall web app with HTTP, WebSocket game state, optional Google
sign-in, and SQLite-backed saved packs.

## Local Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Open `http://localhost:3000`.

## Environment

```bash
HOST=0.0.0.0
PORT=3000
DB_PATH=./spyfall.db
GOOGLE_CLIENT_ID=
```

`GOOGLE_CLIENT_ID` is optional. If it is empty, sign-in is disabled and the game
still runs.

## VPS Deployment

See [docs/VPS_DEPLOYMENT.md](docs/VPS_DEPLOYMENT.md) for Docker Compose,
systemd, and nginx deployment examples.

The important production settings are:

```bash
HOST=127.0.0.1
PORT=3000
DB_PATH=/var/lib/spyfall-web/spyfall.db
```

Use `HOST=127.0.0.1` when nginx is the public entrypoint. Use `HOST=0.0.0.0`
inside Docker.

## Health Check

```bash
curl http://127.0.0.1:3000/healthz
```

The endpoint returns `ok` when the server is running.
