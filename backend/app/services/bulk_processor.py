import csv
import io
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.db.supabase_client import get_service_client
from app.services.figma_client import FigmaClient
from app.services.placeholder_validator import REQUIRED_FIELDS

logger = logging.getLogger(__name__)


class BulkProcessor:
    def __init__(self) -> None:
        self.db = get_service_client()
        self.figma = FigmaClient()

    def create_job(self, name: str, pack_id: UUID, user_id: str) -> dict:
        response = (
            self.db.table("bulk_jobs")
            .insert({"name": name, "pack_id": str(pack_id), "created_by": user_id, "status": "DRAFT"})
            .execute()
        )
        return response.data[0]

    def upload_csv(self, job_id: UUID, csv_bytes: bytes) -> dict:
        decoded = csv_bytes.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))
        rows = []
        for idx, row in enumerate(reader):
            rows.append(
                {
                    "job_id": str(job_id),
                    "row_index": idx,
                    "mapped_data": row,
                    "validation_status": "VALID",
                    "validation_errors": [],
                }
            )
        if rows:
            self.db.table("bulk_job_rows").insert(rows).execute()
        return {"rows_ingested": len(rows)}

    def save_mapping(self, job_id: UUID, mappings: list[dict]) -> dict:
        payload = {"job_id": str(job_id), "mapping": mappings}
        upsert = self.db.table("bulk_job_mappings").upsert(payload, on_conflict="job_id").execute()
        return upsert.data[0]

    def get_rows(self, job_id: UUID) -> list[dict]:
        response = self.db.table("bulk_job_rows").select("*").eq("job_id", str(job_id)).order("row_index").execute()
        return response.data

    async def generate(self, job_id: UUID, overwrite_existing: bool = False) -> dict:
        job_result = self.db.table("bulk_jobs").select("*").eq("id", str(job_id)).single().execute()
        job = job_result.data
        if not job:
            raise HTTPException(status_code=404, detail="Bulk job not found")

        self.db.table("bulk_jobs").update({"status": "PROCESSING"}).eq("id", str(job_id)).execute()

        active_templates = (
            self.db.table("templates")
            .select("*")
            .eq("pack_id", job["pack_id"])
            .eq("status", "APPROVED")
            .eq("is_active", True)
            .execute()
            .data
        )

        if not active_templates:
            raise HTTPException(status_code=400, detail="No active templates for selected pack")

        rows = self.get_rows(job_id)
        output_rows = []
        for row in rows:
            row_data = row["mapped_data"]
            for template in active_templates:
                required_placeholders = REQUIRED_FIELDS[template["template_type"]]
                for placeholder, kind in required_placeholders.items():
                    value = row_data.get(placeholder.strip("{}"), "")
                    if kind == "TEXT":
                        await self.figma.update_text_node(template["figma_file_key"], template["figma_node_id"], value)
                    else:
                        await self.figma.update_image_fill(template["figma_file_key"], template["figma_node_id"], value)
                asset_url = await self.figma.export_node_png(template["figma_file_key"], template["figma_node_id"])
                output_rows.append(
                    {
                        "job_id": str(job_id),
                        "row_id": row["id"],
                        "template_id": template["id"],
                        "size": template["size"],
                        "asset_url": asset_url,
                    }
                )

        if output_rows:
            if overwrite_existing:
                self.db.table("bulk_job_outputs").delete().eq("job_id", str(job_id)).execute()
            self.db.table("bulk_job_outputs").insert(output_rows).execute()

        self.db.table("bulk_jobs").update(
            {"status": "COMPLETED", "completed_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(job_id)).execute()

        return {"job_id": str(job_id), "status": "COMPLETED", "assets_generated": len(output_rows)}

    def status(self, job_id: UUID) -> dict:
        response = self.db.table("bulk_jobs").select("id,status,created_at,completed_at").eq("id", str(job_id)).single().execute()
        return response.data
