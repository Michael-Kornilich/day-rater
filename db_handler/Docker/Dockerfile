# syntax=docker/dockerfile:1-labs
FROM dayrater-base-image

# /app/db_handler/...
WORKDIR db_handler/

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY --exclude="docx.md" --exclude="Docker/" --exclude="requirements.txt" . .

CMD ["fastapi", "run", "--port", "8000", "db_handler.py"]
