### IMPORTANT: the base image from `.base-image` must be built before building these instructions

**Build & run in the compose.yaml with**

```yaml
  services:
    ...:

    data-analyzer:
      build:
        # microservice's directory
        context: "data_analyzer/"

        # path to the dockerfile of the db handler
        dockerfile: "Docker/Dockerfile"

      container_name: "data-analyser"
      ports:
        # currently only visible to the host, change later to 8001:8000 to keep the container in docker network
        - "127.0.0.1:8001:8000"

      environment:
        CONTAINER_NAME: "data_analyzer"

      develop:
        # for faster development 
        watch:
          - path: "data_analyzer/data_analyzer.py"
            target: "/app/data_analyzer/data_analyzer.py"
            action: sync+restart

          - path: "data_analyzer/routing.py"
            target: "/app/data_analyzer/routing.py"

          - path: "Docker/Dockerfile"
            action: rebuild
```
