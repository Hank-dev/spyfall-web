# VPS Deployment

Spyfall Web is a single Python process that serves both static files and
WebSockets on one port. It stores sign-in sessions and saved custom packs in
SQLite.

## Option 1: Docker Compose

1. Create `.env` from `.env.example`:

```bash
cp .env.example .env
editor .env
```

2. Build and start:

```bash
docker compose up -d --build
```

3. Check it:

```bash
curl http://127.0.0.1:3000/healthz
docker compose logs -f spyfall-web
```

The Compose file stores SQLite data in the `spyfall-data` named volume.

## Option 2: Native Python + systemd

These examples use:

- App directory: `/opt/spyfall-web`
- Environment file: `/etc/spyfall-web/spyfall-web.env`
- SQLite data directory: `/var/lib/spyfall-web`
- Service user: `spyfall`

Create the user and directories:

```bash
sudo useradd --system --create-home --home-dir /opt/spyfall-web --shell /usr/sbin/nologin spyfall
sudo mkdir -p /etc/spyfall-web /var/lib/spyfall-web
sudo chown -R spyfall:spyfall /opt/spyfall-web /var/lib/spyfall-web
```

Place this repository at `/opt/spyfall-web`, then install dependencies:

```bash
cd /opt/spyfall-web
sudo -u spyfall python3.12 -m venv .venv
sudo -u spyfall .venv/bin/pip install --upgrade pip
sudo -u spyfall .venv/bin/pip install -r requirements.txt
```

Create the environment file:

```bash
sudo install -m 640 -o root -g spyfall deploy/spyfall-web.env.example /etc/spyfall-web/spyfall-web.env
sudo editor /etc/spyfall-web/spyfall-web.env
```

Recommended native values:

```bash
HOST=127.0.0.1
PORT=3000
DB_PATH=/var/lib/spyfall-web/spyfall.db
```

Install and start systemd:

```bash
sudo cp deploy/systemd/spyfall-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now spyfall-web.service
sudo systemctl status spyfall-web.service
```

Check logs:

```bash
journalctl -u spyfall-web.service -n 100 --no-pager
```

## nginx Reverse Proxy

The app needs WebSocket upgrade headers. Copy the included nginx config and
replace `example.com` with your real domain:

```bash
sudo cp deploy/nginx/spyfall-web.conf /etc/nginx/sites-available/spyfall-web
sudo editor /etc/nginx/sites-available/spyfall-web
sudo ln -s /etc/nginx/sites-available/spyfall-web /etc/nginx/sites-enabled/spyfall-web
sudo nginx -t
sudo systemctl reload nginx
```

For HTTPS, install a certificate with your preferred ACME client. With Certbot:

```bash
sudo certbot --nginx -d your-domain.example
```

The frontend automatically uses `wss://` when the page is served over HTTPS.

## Google Sign-In

If you use Google sign-in, set:

```bash
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
```

In Google Cloud Console, add the production origin:

```text
https://your-domain.example
```

to the OAuth client allowed JavaScript origins.

## Persistence

Back up this file:

```bash
/var/lib/spyfall-web/spyfall.db
```

That SQLite database stores users, sessions, and saved custom packs. Live game
rooms are in memory and reset when the process restarts.
