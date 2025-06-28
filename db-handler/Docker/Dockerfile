FROM base-image:day-rater

WORKDIR db-handler/

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY ../ .

CMD ["fastapi", "run", "--port", "8000", "db-handler.py"]
