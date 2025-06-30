### IMPORTANT: the base image with the name `base-image` must be built before building these instructions

**Build alone with**\
`docker build -t db-handler <path-to-this-directory>`

**Run alone with**\
`docker run --name db-handler -p 127.0.0.1:8000:8000 -v <path-to-db-on-host>:/db/db.csv db-handler:day-rater`

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
        # currently only visible to the host, change later to close
        - "127.0.0.1:8000:8000"
      volumes:
        # Database bind. CHANGE when not running on this device
        - "/Users/Misha/Documents/python_projects/day-rater-db/db.csv:/db/db.csv"

      develop:
        watch:
          # relative path to the script with project being the root
          - path: "db-handler/db-handler.py"
            target: "/app/db-handler/db-handler.py"
            action: sync+restart
```