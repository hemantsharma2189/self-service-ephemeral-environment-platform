import re

from preview_env.models import (
    EnvironmentPlan,
    EnvironmentStatus,
    PreviewEnvironmentRequest,
)


def create_environment_plan(
    request: PreviewEnvironmentRequest,
    base_domain: str = "preview.local",
) -> EnvironmentPlan:
    repository_slug = re.sub(
        r"[^a-z0-9-]",
        "-",
        request.repository.lower(),
    ).strip("-")

    environment_name = f"{repository_slug}-pr-{request.pull_request_number}"
    namespace = f"preview-pr-{request.pull_request_number}"
    preview_url = f"https://pr-{request.pull_request_number}.{base_domain}"

    policy_decisions = [
        "Immutable container image tag accepted.",
        f"TTL of {request.ttl_hours} hours is within policy.",
        "Dedicated Kubernetes namespace planned.",
        "Automatic cleanup is required after expiration.",
    ]

    if request.dry_run:
        policy_decisions.append("Dry-run mode enabled; no Kubernetes resources will be created.")

    return EnvironmentPlan(
        environment_name=environment_name,
        namespace=namespace,
        preview_url=preview_url,
        image=request.image,
        owner=request.owner,
        pull_request_number=request.pull_request_number,
        ttl_hours=request.ttl_hours,
        status=EnvironmentStatus.PLANNED,
        dry_run=request.dry_run,
        policy_decisions=policy_decisions,
    )
