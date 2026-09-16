import pytest
from pydantic import ValidationError

from preview_env.models import PreviewEnvironmentRequest
from preview_env.planner import create_environment_plan


def create_request(
    image: str = "nginx:1.27.5-alpine",
) -> PreviewEnvironmentRequest:
    return PreviewEnvironmentRequest(
        repository="sample-cloud-application",
        pull_request_number=42,
        commit_sha="a1b2c3d4e5f678901234567890abcdef12345678",
        image=image,
        owner="hemant-sharma",
        ttl_hours=8,
        dry_run=True,
    )


def test_environment_plan_uses_pull_request_identity() -> None:
    plan = create_environment_plan(create_request())

    assert plan.environment_name == "sample-cloud-application-pr-42"
    assert plan.namespace == "preview-pr-42"
    assert plan.preview_url == "https://pr-42.preview.local"
    assert plan.dry_run is True


def test_latest_container_tag_is_rejected() -> None:
    with pytest.raises(ValidationError):
        create_request(image="nginx:latest")


def test_ttl_greater_than_policy_limit_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PreviewEnvironmentRequest(
            repository="sample-app",
            pull_request_number=10,
            commit_sha="abcdef1234567890",
            image="nginx:1.27.5-alpine",
            owner="platform-team",
            ttl_hours=100,
        )
