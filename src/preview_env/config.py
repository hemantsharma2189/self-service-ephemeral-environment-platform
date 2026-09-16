from pathlib import Path

import yaml
from pydantic import ValidationError

from preview_env.models import PreviewEnvironmentRequest


class ConfigurationError(Exception):
    """Raised when a preview environment request is invalid."""


def load_request(
    file_path: str | Path,
) -> PreviewEnvironmentRequest:
    path = Path(file_path)

    if not path.exists():
        raise ConfigurationError(f"Request file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as request_file:
            data = yaml.safe_load(request_file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML configuration: {error}") from error

    if not isinstance(data, dict):
        raise ConfigurationError("Request must contain YAML key-value pairs.")

    try:
        return PreviewEnvironmentRequest.model_validate(data)
    except ValidationError as error:
        raise ConfigurationError(f"Request validation failed:\n{error}") from error
