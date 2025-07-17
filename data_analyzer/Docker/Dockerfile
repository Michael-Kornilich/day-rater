# syntax=docker/dockerfile:1-labs
FROM dayrater-base-image

WORKDIR /data_analyzer

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt && \
    mkdir media

COPY --exclude="docs.md" --exclude=Docker --exclude="requirements.txt" . .

CMD ["python", "fastapi", "--port", "8000", "routing.py"]
