#!/bin/bash

exec celery -A config worker -l INFO 
