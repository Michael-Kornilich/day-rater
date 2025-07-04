# syntax=docker/dockerfile:1-labs
FROM dayrater-base-image

WORKDIR /daemon

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY --exclude="Docker/" --exclude="docs.md" --exclude="requirements.txt" . .

CMD ["fastapi", "run", "--port", "8000", "daemon.py"]