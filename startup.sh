#!/usr/bin/env bash
gunicorn -c /config/gunicorn.conf wsgi:app --reload
