from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.schemas import ApprovalAction, TemplateSubmit
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])
service = TemplateService()


@router.post("/submit")
async def submit_template(payload: TemplateSubmit, user=Depends(get_current_user)):
    return await service.submit(payload.model_dump(), user["sub"])


@router.get("/pending")
def get_pending_templates(_: dict = Depends(get_current_user)):
    return service.list_pending()


@router.post("/{template_id}/approve")
def approve_template(template_id: UUID, _: ApprovalAction, user=Depends(get_current_user)):
    return service.approve(template_id, user["sub"])


@router.post("/{template_id}/reject")
def reject_template(template_id: UUID, payload: ApprovalAction, user=Depends(get_current_user)):
    return service.reject(template_id, user["sub"], payload.reason or "No reason provided")


@router.post("/{template_id}/activate")
def activate_template(template_id: UUID, user=Depends(get_current_user)):
    _ = user
    return service.activate(template_id)
