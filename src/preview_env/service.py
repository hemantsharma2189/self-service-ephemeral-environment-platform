import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from preview_env.cost import estimate_environment_cost
from preview_env.models import PreviewEnvironmentRequest
from preview_env.planner import create_environment_plan
from preview_env.renderer import render_kubernetes_manifests


def generate_environment_artifacts(
    request: PreviewEnvironmentRequest,
    output_directory: str | Path = "artifacts",
) -> dict[str, Path]:
    plan = create_environment_plan(request)
    cost = estimate_environment_cost(request)
    manifests = render_kubernetes_manifests(
        request=request,
        plan=plan,
    )

    environment_directory = Path(output_directory) / plan.environment_name
    environment_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    plan_path = environment_directory / "plan.json"
    manifests_path = environment_directory / "manifests.yaml"
    summary_path = environment_directory / "summary.md"

    plan_data = {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": plan.model_dump(mode="json"),
        "cost_estimate": asdict(cost),
    }

    plan_path.write_text(
        json.dumps(plan_data, indent=2),
        encoding="utf-8",
    )
    manifests_path.write_text(
        manifests,
        encoding="utf-8",
    )

    policy_list = "\n".join(f"- {decision}" for decision in plan.policy_decisions)

    summary = f"""# Preview Environment Plan

## Environment

- **Name:** {plan.environment_name}
- **Namespace:** {plan.namespace}
- **Pull request:** #{plan.pull_request_number}
- **Owner:** {plan.owner}
- **Image:** `{plan.image}`
- **Preview URL:** {plan.preview_url}
- **TTL:** {plan.ttl_hours} hours
- **Execution mode:** {"Dry run" if plan.dry_run else "Live"}

## Policy decisions

{policy_list}

## Estimated cost

- **CPU:** ${cost.cpu_cost}
- **Memory:** ${cost.memory_cost}
- **Estimated total:** ${cost.total_estimated_cost} {cost.currency}

> This is a planning estimate and not an actual cloud bill.
"""

    summary_path.write_text(
        summary,
        encoding="utf-8",
    )

    return {
        "plan": plan_path,
        "manifests": manifests_path,
        "summary": summary_path,
    }
