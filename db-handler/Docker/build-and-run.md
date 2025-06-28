### IMPORTANT: the base image with the name `base-image:day-rater` must be built before building these instructions

**Build with**\
`docker build -t db-handler:day-rater <path-to-this-directory>`

**Run with**\
`docker run --name db-handler -p 127.0.0.1:8000:8000 -v <path-to-db-on-host>:/db/db.csv db-handler:day-rater`