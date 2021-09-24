#!/bin/bash

exec celery -A config beat
