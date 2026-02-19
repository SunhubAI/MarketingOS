import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.db.supabase_client import get_service_client
from app.services.figma_client import FigmaClient
from app.services.placeholder_validator import validate_template_contract

logger = logging.getLogger(__name__)


class TemplateService:
    def __init__(self) -> None:
        self.db = get_service_client()
        self.figma = FigmaClient()

    async def submit(self, payload: dict, user_id: str) -> dict:
        file_key, node_id = self.figma.parse_figma_url(payload["figma_url"])
        node_payload = await self.figma.get_file_nodes(file_key, node_id)
        node = node_payload["nodes"][node_id]["document"]
        placeholders = self.figma.extract_placeholders_from_tree(node)
        report = validate_template_contract(payload["template_type"], placeholders)
        preview = await self.figma.get_node_preview_image(file_key, node_id)

        insert_payload = {
            "template_name": payload["template_name"],
            "template_type": payload["template_type"],
            "pack_id": str(payload["pack_id"]),
            "size": payload["size"],
            "version": payload["version"],
            "status": "DRAFT",
            "is_active": False,
            "figma_file_key": file_key,
            "figma_node_id": node_id,
            "detected_placeholders": placeholders,
            "validation_report": report,
            "preview_image_url": preview,
            "created_by": user_id,
        }
        response = self.db.table("templates").insert(insert_payload).execute()
        return response.data[0]

    def list_pending(self) -> list[dict]:
        response = (
            self.db.table("templates")
            .select("*")
            .eq("status", "DRAFT")
            .order("created_at", desc=False)
            .execute()
        )
        return response.data

    def approve(self, template_id: UUID, admin_id: str) -> dict:
        payload = {
            "status": "APPROVED",
            "approved_by": admin_id,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "rejected_reason": None,
        }
        response = self.db.table("templates").update(payload).eq("id", str(template_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Template not found")
        return response.data[0]

    def reject(self, template_id: UUID, admin_id: str, reason: str) -> dict:
        response = (
            self.db.table("templates")
            .update(
                {
                    "status": "REJECTED",
                    "approved_by": admin_id,
                    "rejected_reason": reason,
                    "approved_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            .eq("id", str(template_id))
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Template not found")
        return response.data[0]

    def activate(self, template_id: UUID) -> dict:
        response = self.db.rpc("activate_template", {"template_uuid": str(template_id)}).execute()
        if response.data is None:
            raise HTTPException(status_code=400, detail="Activation failed")
        return {"activated": True, "template_id": str(template_id)}
