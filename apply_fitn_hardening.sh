#!/usr/bin/env bash
set -euo pipefail

# --- locate main FastAPI app file ---
MAIN_FILE="$(grep -RIl --include='*.py' -E 'app\s*=\s*FastAPI\(' app || true | head -n1)"
if [[ -z "${MAIN_FILE}" ]]; then
  echo "Could not find FastAPI app file. Adjust MAIN_FILE manually."
  exit 1
fi
echo "Using main file: ${MAIN_FILE}"

# --- add /healthz router ---
mkdir -p app/routers
cat > app/routers/health.py <<'PY'
from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz", include_in_schema=False)
async def healthz():
    return {"ok": True}
PY

# --- include router import + registration (idempotent) ---
if ! grep -q "from .routers import health as health_router" "$MAIN_FILE"; then
  awk '
    BEGIN{i=0}
    /from[[:space:]]+fastapi/ && i==0 {print; print "from .routers import health as health_router"; i=1; next}
    {print}
  ' "$MAIN_FILE" > "$MAIN_FILE.tmp" && mv "$MAIN_FILE.tmp" "$MAIN_FILE"
fi

if ! grep -q "include_router(health_router.router" "$MAIN_FILE"; then
  # insert after app = FastAPI(...)
  awk '
    BEGIN{added=0}
    {print}
    /app[[:space:]]*=[[:space:]]*FastAPI\(/ && added==0 {
      print "";
      print "app.include_router(health_router.router)";
      added=1
    }
  ' "$MAIN_FILE" > "$MAIN_FILE.tmp" && mv "$MAIN_FILE.tmp" "$MAIN_FILE"
fi

# --- test for healthz ---
mkdir -p tests
cat > tests/test_healthz.py <<'PY'
from fastapi.testclient import TestClient
from app.main import app  # adjust if your app object lives elsewhere

def test_healthz():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("ok") is True
PY

# --- .env.example (no secrets) ---
cat > .env.example <<'ENV'
# ---- Application ----
APP_ENV=dev
APP_SECRET=change_me
ALLOWED_ORIGINS=http://localhost,http://localhost:81,https://dev.mvconways.com:81
COOKIE_SECURE=false
COOKIE_MAX_AGE=2592000

# ---- Database ----
MONGO_URI=mongodb://mongo:27017/fitn

# ---- Nginx ----
SERVER_NAME=fitn.local
ENV

# --- pre-commit (skip if exists) ---
if [[ ! -f .pre-commit-config.yaml ]]; then
  cat > .pre-commit-config.yaml <<'YAML'
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
YAML
fi

# --- nginx security headers + proxy sanity (include this file in server { } ) ---
mkdir -p nginx
cat > nginx/security_headers.conf <<'NGINX'
# Security headers
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
# Enable HSTS only on HTTPS sites
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# In your main location / { } block also ensure:
# proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# proxy_set_header X-Forwarded-Proto $scheme;
# proxy_read_timeout 60s;
NGINX

# --- docker-compose: ensure internal/public networks & healthchecks ---
COMPOSE_FILE=""
for f in docker-compose.yaml docker-compose.yml; do
  if [[ -f "$f" ]]; then COMPOSE_FILE="$f"; break; fi
done
[[ -z "$COMPOSE_FILE" ]] && COMPOSE_FILE="docker-compose.yaml"

cp -a "$COMPOSE_FILE" "${COMPOSE_FILE}.bak.$(date +%s)"

cat > "${COMPOSE_FILE}.new" <<'YAML'
services:
  api:
    build: ./app
    env_file: .env
    depends_on:
      - mongo
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8002/healthz"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks: ["internal"]

  mongo:
    image: mongo:7
    volumes: ["mongo-data:/data/db"]
    networks: ["internal"]

  nginx:
    build: ./nginx
    ports: ["80:80"]
    depends_on: ["api"]
    networks: ["internal", "public"]

volumes:
  mongo-data:

networks:
  internal:
  public:
YAML

mv -f "${COMPOSE_FILE}.new" "$COMPOSE_FILE"

# --- report any set_cookie sites to manually review (safer than blind sed) ---
echo "Potential cookie setters (review for HttpOnly/SameSite/Secure):"
grep -RIn --include='*.py' "set_cookie(" app || true

echo "Done."
