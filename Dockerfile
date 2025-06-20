# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13.4
FROM python:${PYTHON_VERSION}-alpine3.22

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Intstall potentially missing dependencies for scientific libraries
# RUN --mount=type=cache,target=/root/.cache/alpine \
#     apk add --no-cache gcc

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Run the application.
CMD gunicorn '.venv.lib.python3.13.site-packages.fastapi.middleware.wsgi' --bind=0.0.0.0:8000
