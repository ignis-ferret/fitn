FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn pymongo openai python-dotenv jinja2 aiofiles motor python-multipart
CMD ["uvicorn", "main:app","--host", "0.0.0.0","--port", "8002","--proxy-headers","--forwarded-allow-ips", "*"]
