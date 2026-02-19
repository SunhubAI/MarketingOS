from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.auth import get_current_user
from app.models.schemas import BulkJobCreate, BulkJobMapRequest, GenerateRequest
from app.services.bulk_processor import BulkProcessor

router = APIRouter(prefix="/bulk-jobs", tags=["bulk-jobs"])
processor = BulkProcessor()


@router.post("")
def create_bulk_job(payload: BulkJobCreate, user=Depends(get_current_user)):
    return processor.create_job(payload.name, payload.pack_id, user["sub"])


@router.post("/{job_id}/upload")
async def upload_csv(job_id: UUID, file: UploadFile = File(...), _: dict = Depends(get_current_user)):
    raw = await file.read()
    return processor.upload_csv(job_id, raw)


@router.post("/{job_id}/map")
def map_bulk_job(job_id: UUID, payload: BulkJobMapRequest, _: dict = Depends(get_current_user)):
    return processor.save_mapping(job_id, [entry.model_dump() for entry in payload.mappings])


@router.get("/{job_id}/rows")
def get_bulk_rows(job_id: UUID, _: dict = Depends(get_current_user)):
    return processor.get_rows(job_id)


@router.post("/{job_id}/generate")
async def generate_bulk(job_id: UUID, payload: GenerateRequest, _: dict = Depends(get_current_user)):
    return await processor.generate(job_id, overwrite_existing=payload.overwrite_existing)


@router.get("/{job_id}/status")
def get_status(job_id: UUID, _: dict = Depends(get_current_user)):
    return processor.status(job_id)
