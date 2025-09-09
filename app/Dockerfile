FROM python:3.11

# Optional: faster/cleaner pip installs
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Put the code in /srv/app so the package name is "app"
WORKDIR /srv
COPY . /srv/app

# Install Python deps (consider a requirements.txt later)
RUN pip install fastapi uvicorn pymongo openai python-dotenv jinja2 aiofiles motor python-multipart

# Healthcheck in compose uses wget; python:3.11 may not have it. Install one of wget/curl.
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# Run by module path so relative imports work
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--proxy-headers", "--forwarded-allow-ips", "*"]
