### IMPORTANT: the base image from `.base-image` must be built before building these instructions

**Build & run in the compose.yaml with**

```yaml
  services:
    ...:

    daemon:
      build:
        # microservice's directory
        context: "daemon/"

        # path to the dockerfile of the db handler
        dockerfile: "Docker/Dockerfile"

      container_name: "daemon"
      ports:
        # currently only visible to the host, change later to 8000:8000 to keep the container in docker network
        - "127.0.0.1:8001:8000"

      environment:
        CONTAINER_NAME: "daemon"


      develop:
        # for faster development 
        watch:
          - path: "daemon/daemon.py"
            target: "/app/daemon/daemon.py"
            action: sync+restart

          - path: "Docker/Dockerfile"
            action: rebuild

          - path: "daemon/tests/*" # might not work
            target: "/app/db_handler/tests/*" # might not work
            action: sync+restart
```