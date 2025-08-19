# app/template_loader.py
from pathlib import Path
from starlette.templating import Jinja2Templates
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals['now'] = datetime.utcnow  # for base.html footer
