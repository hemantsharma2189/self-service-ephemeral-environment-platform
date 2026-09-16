from dataclasses import dataclass

from preview_env.models import PreviewEnvironmentRequest


@dataclass(frozen=True)
class CostEstimate:
    cpu_cost: float
    memory_cost: float
    total_estimated_cost: float
    ttl_hours: int
    currency: str = "USD"


def parse_cpu_cores(cpu_value: str) -> float:
    if cpu_value.endswith("m"):
        return float(cpu_value[:-1]) / 1000

    return float(cpu_value)


def parse_memory_gib(memory_value: str) -> float:
    units = {
        "Ki": 1 / (1024 * 1024),
        "Mi": 1 / 1024,
        "Gi": 1,
    }

    for unit, multiplier in units.items():
        if memory_value.endswith(unit):
            amount = float(memory_value[: -len(unit)])
            return amount * multiplier

    raise ValueError("Memory must use Ki, Mi, or Gi units.")


def estimate_environment_cost(
    request: PreviewEnvironmentRequest,
    cpu_hourly_rate: float = 0.04,
    memory_gib_hourly_rate: float = 0.005,
) -> CostEstimate:
    cpu_cores = parse_cpu_cores(request.resources.cpu_limit)
    memory_gib = parse_memory_gib(request.resources.memory_limit)

    cpu_cost = cpu_cores * cpu_hourly_rate * request.ttl_hours
    memory_cost = memory_gib * memory_gib_hourly_rate * request.ttl_hours

    return CostEstimate(
        cpu_cost=round(cpu_cost, 4),
        memory_cost=round(memory_cost, 4),
        total_estimated_cost=round(
            cpu_cost + memory_cost,
            4,
        ),
        ttl_hours=request.ttl_hours,
    )
