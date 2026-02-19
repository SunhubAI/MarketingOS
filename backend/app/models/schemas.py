from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

TemplateType = Literal["PRODUCT", "BLOG", "CAMPAIGN", "PARTNER", "EVENT"]
TemplateStatus = Literal["DRAFT", "APPROVED", "REJECTED", "ARCHIVED"]
SizeType = Literal["IG_4x5", "LINKEDIN_1x1", "STORY_9x16", "BANNER_1400x170"]


class PackCreate(BaseModel):
    name: str
    required_sizes: list[SizeType]


class Pack(BaseModel):
    id: UUID
    name: str
    required_sizes: list[SizeType]


class TemplateSubmit(BaseModel):
    template_name: str
    template_type: TemplateType
    pack_id: UUID
    size: SizeType
    version: int
    figma_url: str


class ApprovalAction(BaseModel):
    reason: str | None = None


class TemplateOut(BaseModel):
    id: UUID
    template_name: str
    template_type: TemplateType
    pack_id: UUID
    size: SizeType
    version: int
    status: TemplateStatus
    is_active: bool
    figma_file_key: str
    figma_node_id: str
    detected_placeholders: list[dict[str, Any]]
    validation_report: dict[str, Any]
    preview_image_url: str | None
    created_by: UUID
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    rejected_reason: str | None = None


class BulkJobCreate(BaseModel):
    name: str
    pack_id: UUID


class MappingRule(BaseModel):
    source: str = Field(description="CSV column, static:<value>, or placeholder")
    placeholder: str


class BulkJobMapRequest(BaseModel):
    mappings: list[MappingRule]


class GenerateRequest(BaseModel):
    overwrite_existing: bool = False


class BulkJobOut(BaseModel):
    id: UUID
    name: str
    pack_id: UUID
    created_by: UUID
    status: Literal["DRAFT", "PROCESSING", "COMPLETED", "FAILED"]
