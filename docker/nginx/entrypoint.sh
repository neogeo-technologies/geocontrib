#!/bin/bash

envsubst '$$URL_PREFIX' < /etc/nginx/conf.d/geocontrib.template > /etc/nginx/conf.d/default.conf
exec "$@"
