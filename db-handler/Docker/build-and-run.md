### IMPORTANT: the base image from `.base-image` must be built before building these instructions

**Build & run in the compose.yaml with**

```yaml
  services:
    ...:

    db-handler:
      build:
        # microservice's directory
        context: "db-handler/"

        # path to the dockerfile of the db handler
        dockerfile: "Docker/Dockerfile"

      container_name: "db-handler"
      ports:
        # currently only visible to the host, change later to 8000:8000 to keep the container in docker network
        - "127.0.0.1:8000:8000"

      # mostly for testing purposes, to hijack the path 
      # when changing copy the path into volumes after :
      environment:
        INTERNAL_DB_PATH: "/db/db.csv"
      volumes:
        # Database bind. CHANGE when not running on this device
        - "/Users/Misha/Documents/python_projects/day-rater-db/db.csv:/db/db.csv"

      develop:
        # relative paths to the scripts with project being the root
        watch:
          - path: "db-handler/db-handler.py"
            target: "/app/db-handler/db-handler.py"
            action: sync+restart

          - path: "db-handler/utility.py"
            target: "/app/db-handler/utility.py"
            action: sync+restart
```