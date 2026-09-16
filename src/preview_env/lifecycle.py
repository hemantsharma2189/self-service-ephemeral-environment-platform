from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from preview_env.models import EnvironmentPlan


@dataclass(frozen=True)
class CleanupDecision:
    should_delete: bool
    reason: str
    expires_at: datetime


def calculate_expiration(
    created_at: datetime,
    ttl_hours: int,
) -> datetime:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    return created_at + timedelta(hours=ttl_hours)


def evaluate_cleanup(
    plan: EnvironmentPlan,
    created_at: datetime,
    pull_request_open: bool,
    current_time: datetime | None = None,
) -> CleanupDecision:
    now = current_time or datetime.now(UTC)

    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    expires_at = calculate_expiration(
        created_at=created_at,
        ttl_hours=plan.ttl_hours,
    )

    if not pull_request_open:
        return CleanupDecision(
            should_delete=True,
            reason="Pull request is closed.",
            expires_at=expires_at,
        )

    if now >= expires_at:
        return CleanupDecision(
            should_delete=True,
            reason="Environment TTL has expired.",
            expires_at=expires_at,
        )

    return CleanupDecision(
        should_delete=False,
        reason="Environment is active and within its TTL.",
        expires_at=expires_at,
    )
