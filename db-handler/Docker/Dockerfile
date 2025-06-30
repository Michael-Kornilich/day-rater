FROM dayrater-base-image

# /app/db-handler/...
WORKDIR db-handler/

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY db-handler.py utility.py ./

CMD ["fastapi", "run", "--port", "8000", "db-handler.py"]
