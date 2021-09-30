#!/bin/bash

exec celery -A config beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
