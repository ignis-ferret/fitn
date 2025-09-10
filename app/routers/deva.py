# app/routers/deva.py
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from ..deps import require_login_redirect
from ..services.audit import log_prompt_response
from ..services.openai_service import ask_chatgpt
from ..template_loader import templates  # ✅ shared env

router = APIRouter(prefix="/deva")


@router.get("/", response_class=HTMLResponse)
async def dev_page(request: Request, _u=Depends(require_login_redirect)):
    return templates.TemplateResponse("deva.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def handle_prompt(
    request: Request, prompt: str = Form(...), _u=Depends(require_login_redirect)
):
    response = await ask_chatgpt(prompt)
    await log_prompt_response(prompt, response)
    return templates.TemplateResponse(
        "deva.html", {"request": request, "prompt": prompt, "response": response}
    )
