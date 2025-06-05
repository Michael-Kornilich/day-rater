# Day rater

**Goal:** gain insights into what influences welfare

## MVP

1. `python run.py --rank <rating>` - updates the db with the rating and background pulling of other data
2. `python run.py --analyze` - analyzes the data in the db and create statistics and visualizations of the
   dependencies

## Features down the line

* Comparison between people's ratings
* Ability to generate posts for social media
* ChatGPT for text parsing
* Telegram / whatsapp bot
* Send notifications when forgetting to track

## Technical
* Pull weather data like overcast, pressure, and wind. Compare them to the rating
* Host a lightweight database

* Tasks of the daemon
  * calling the APIs
  * writing to the db
  * calling the analyzer script

