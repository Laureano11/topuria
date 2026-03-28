from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.dashboard import build_dashboard_context
from app.db import get_session


router = APIRouter()


@router.get("/")
def home(
    request: Request,
    tab: str = "weekly",
    session: Session = Depends(get_session),
):
    templates = request.app.state.templates
    context = build_dashboard_context(session, tab)
    context["request"] = request
    return templates.TemplateResponse("base.html", context)


@router.get("/day")
def day_redirect() -> RedirectResponse:
    return RedirectResponse(url="/?tab=weekly", status_code=303)


@router.get("/week")
def week_redirect() -> RedirectResponse:
    return RedirectResponse(url="/?tab=weekly", status_code=303)


@router.get("/month")
def month_redirect() -> RedirectResponse:
    return RedirectResponse(url="/?tab=monthly", status_code=303)


@router.get("/year")
def year_redirect() -> RedirectResponse:
    return RedirectResponse(url="/?tab=yearly", status_code=303)
