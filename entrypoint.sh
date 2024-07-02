#!/bin/sh
export FLASK_APP=run:app

# Init database
flask --app run init-db

# Run
gunicorn -b 0.0.0.0:5000 --worker-class eventlet -w 1 run:app