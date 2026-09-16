from datetime import UTC, datetime, timedelta

from preview_env.models import PreviewEnvironmentRequest
from preview_env.lifecycle import evaluate_cleanup
from preview_env.planner import create_environment_plan


def create_plan():
    request = PreviewEnvironmentRequest(
        repository="sample-app",
        pull_request_number=42,
        commit_sha="abcdef1234567890",
        image="nginx:1.27.5-alpine",
        owner="platform-team",
        ttl_hours=8,
        dry_run=True,
    )
    return create_environment_plan(request)


def test_active_environment_is_not_deleted() -> None:
    created_at = datetime(2026, 9, 16, 8, 0, tzinfo=UTC)
    current_time = created_at + timedelta(hours=2)

    decision = evaluate_cleanup(
        plan=create_plan(),
        created_at=created_at,
        pull_request_open=True,
        current_time=current_time,
    )

    assert decision.should_delete is False
    assert "active" in decision.reason.lower()


def test_expired_environment_is_deleted() -> None:
    created_at = datetime(2026, 9, 16, 8, 0, tzinfo=UTC)
    current_time = created_at + timedelta(hours=9)

    decision = evaluate_cleanup(
        plan=create_plan(),
        created_at=created_at,
        pull_request_open=True,
        current_time=current_time,
    )

    assert decision.should_delete is True
    assert "expired" in decision.reason.lower()


def test_closed_pull_request_triggers_cleanup() -> None:
    created_at = datetime(2026, 9, 16, 8, 0, tzinfo=UTC)

    decision = evaluate_cleanup(
        plan=create_plan(),
        created_at=created_at,
        pull_request_open=False,
        current_time=created_at + timedelta(hours=1),
    )

    assert decision.should_delete is True
    assert "closed" in decision.reason.lower()
