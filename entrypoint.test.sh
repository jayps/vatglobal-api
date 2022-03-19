#!/usr/bin/env bash
python manage.py migrate
coverage run --source='.' manage.py test
coverage html
coverage report