import logging
import re
from urllib.parse import urlparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class FigmaClient:
    def __init__(self) -> None:
        self.base_url = settings.figma_api_base_url
        self.headers = {"X-Figma-Token": settings.figma_api_key}

    @staticmethod
    def parse_figma_url(figma_url: str) -> tuple[str, str]:
        parsed = urlparse(figma_url)
        match = re.search(r"/file/([a-zA-Z0-9]+)", parsed.path)
        node_match = re.search(r"node-id=([^&]+)", parsed.query)
        if not match or not node_match:
            raise ValueError("Invalid Figma URL. Expected file key and node-id query parameter.")
        return match.group(1), node_match.group(1)

    async def get_file_nodes(self, file_key: str, node_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/files/{file_key}/nodes",
                params={"ids": node_id},
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    def extract_placeholders_from_tree(self, node: dict) -> list[dict]:
        placeholders: list[dict] = []

        def walk(current: dict) -> None:
            name = current.get("name", "")
            node_type = current.get("type", "")
            if name.startswith("{{") and name.endswith("}}"):
                node_kind = "TEXT"
                fills = current.get("fills", [])
                if node_type == "RECTANGLE" and fills and any(fill.get("type") == "IMAGE" for fill in fills):
                    node_kind = "IMAGE"
                placeholders.append(
                    {
                        "placeholder": name,
                        "node_id": current.get("id"),
                        "node_type": node_type,
                        "node_kind": node_kind,
                    }
                )
            for child in current.get("children", []):
                walk(child)

        walk(node)
        return placeholders

    async def get_node_preview_image(self, file_key: str, node_id: str) -> str | None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/images/{file_key}",
                params={"ids": node_id, "format": "png"},
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json().get("images", {}).get(node_id)

    async def duplicate_node(self, file_key: str, node_id: str) -> str:
        logger.info("Node duplication should use Figma branch endpoint or file copy workflow")
        return node_id

    async def update_text_node(self, file_key: str, node_id: str, value: str) -> None:
        logger.info("Text update requested file=%s node=%s value=%s", file_key, node_id, value)

    async def update_image_fill(self, file_key: str, node_id: str, image_url: str) -> None:
        logger.info("Image fill update requested file=%s node=%s image_url=%s", file_key, node_id, image_url)

    async def export_node_png(self, file_key: str, node_id: str) -> str | None:
        return await self.get_node_preview_image(file_key, node_id)
