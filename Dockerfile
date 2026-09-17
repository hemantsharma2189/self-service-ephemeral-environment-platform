FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system preview \
    && useradd --system --gid preview --create-home preview

COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples

RUN pip install --upgrade pip \
    && pip install .

RUN mkdir -p /app/artifacts \
    && chown -R preview:preview /app

USER preview

ENTRYPOINT ["preview-env"]
CMD ["examples/preview-request.yaml"]
