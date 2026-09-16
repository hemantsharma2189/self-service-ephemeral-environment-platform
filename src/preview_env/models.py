import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class EnvironmentStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"
    FAILED = "failed"


class ResourceRequirements(BaseModel):
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "256Mi"


class PreviewEnvironmentRequest(BaseModel):
    repository: str
    pull_request_number: int = Field(gt=0)
    commit_sha: str = Field(min_length=7, max_length=40)
    image: str
    owner: str
    ttl_hours: int = Field(default=8, gt=0, le=72)
    container_port: int = Field(default=8080, gt=0, le=65535)
    dry_run: bool = True
    resources: ResourceRequirements = Field(
        default_factory=ResourceRequirements
    )

    @field_validator("repository", "owner")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError(
                "Value may contain only letters, numbers, dots, "
                "underscores, and hyphens."
            )
        return value

    @field_validator("image")
    @classmethod
    def validate_image(cls, value: str) -> str:
        if value.endswith(":latest"):
            raise ValueError(
                "Immutable image tags are required; ':latest' is not allowed."
            )
        return value


class EnvironmentPlan(BaseModel):
    environment_name: str
    namespace: str
    preview_url: str
    image: str
    owner: str
    pull_request_number: int
    ttl_hours: int
    status: EnvironmentStatus
    dry_run: bool
    policy_decisions: list[str] = Field(default_factory=list)
