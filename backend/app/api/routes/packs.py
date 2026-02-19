from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.db.supabase_client import get_service_client
from app.models.schemas import PackCreate

router = APIRouter(prefix="/packs", tags=["packs"])
db = get_service_client()


@router.get("")
def list_packs(_: dict = Depends(get_current_user)):
    return db.table("template_packs").select("*").order("name").execute().data


@router.post("")
def create_pack(payload: PackCreate, _: dict = Depends(get_current_user)):
    return db.table("template_packs").insert(payload.model_dump()).execute().data[0]


@router.get("/{pack_id}/coverage")
def pack_coverage(pack_id: UUID, _: dict = Depends(get_current_user)):
    pack = db.table("template_packs").select("*").eq("id", str(pack_id)).single().execute().data
    templates = (
        db.table("templates")
        .select("size,is_active,status,version")
        .eq("pack_id", str(pack_id))
        .order("size")
        .order("version", desc=True)
        .execute()
        .data
    )
    return {"pack": pack, "templates": templates}
