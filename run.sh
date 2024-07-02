#!/bin/sh

export FLASK_APP=run:app
export FLASK_ENV=development

flask run
