#!/bin/bash

DIR=$APP_PATH/src/docker/docker-entrypoint.d/

if [[ -d "$DIR" ]]
then
    /bin/run-parts --verbose "$DIR"
else
  echo "No docker-entrypoint scripts in $DIR"
fi

exec "$@"
