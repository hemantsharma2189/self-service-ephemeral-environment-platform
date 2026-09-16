from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from preview_env.config import (
    ConfigurationError,
    load_request,
)
from preview_env.cost import estimate_environment_cost
from preview_env.planner import create_environment_plan
from preview_env.service import generate_environment_artifacts

app = typer.Typer(help=("Create secure, temporary Kubernetes preview environment plans."))
console = Console()

@app.command()
def create(
    request_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the YAML preview request.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            help="Directory for generated evidence.",
        ),
    ] = Path("artifacts"),
) -> None:
    try:
        request = load_request(request_file)
        plan = create_environment_plan(request)
        cost = estimate_environment_cost(request)
        artifacts = generate_environment_artifacts(
            request=request,
            output_directory=output,
        )
    except (ConfigurationError, ValueError) as error:
        console.print(f"[red]Preview environment request failed:[/red] {error}")
        raise typer.Exit(code=1) from error

    table = Table(title="Ephemeral Preview Environment Plan")
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Environment", plan.environment_name)
    table.add_row("Namespace", plan.namespace)
    table.add_row("Preview URL", plan.preview_url)
    table.add_row("Image", plan.image)
    table.add_row("TTL", f"{plan.ttl_hours} hours")
    table.add_row(
        "Mode",
        "DRY-RUN" if plan.dry_run else "LIVE",
    )
    table.add_row(
        "Estimated cost",
        f"${cost.total_estimated_cost} {cost.currency}",
    )

    console.print(table)

    for name, path in artifacts.items():
        console.print(f"{name.title()}: {path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
