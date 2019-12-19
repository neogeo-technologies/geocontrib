#!/bin/bash
# --------------------------------------------------------------- #
create_link()
{
    ln -s $1 $2 2> /dev/null
    if [ $? -eq 0 ]; then
        echo "[  OK  ] Link created: ${1}->${2}"
    else
        echo "[FAILED] No such file or directory: ${1}"
        exit 1
    fi
}
# --------------------------------------------------------------- #
echo "Step 01."
cd $APP_PATH/
marker_file="marker_file_step_01"
if [ -f marker_file ]; then
    echo "$marker_file already exists."
else
    django-admin startproject config .

    create_link $SRC/collab/ .
    create_link $SRC/api/ .

    # Preparation spécifique
    # Django
    if [ -f "config/urls.py" ]; then
        rm config/urls.py
    fi
    if [ -f "config/settings.py" ]; then
        rm config/settings.py
    fi
    cp $SRC/docker_data/settings.py config/settings.py
    cp $SRC/docker_data/urls.py config/urls.py

    # Attente du serveur postgres
    echo "Waiting for database..."
    i=1
    while true
    do
        if  $(nc -z ${DB_HOSTNAME} 5432) ; then
            echo "[${DB_HOSTNAME}] The database server is ready."
            break
        fi
        echo "[Retry: $i] The database server is not ready. Next attempt in ${TIME_SLEEP}s"
        sleep $TIME_SLEEP
        ((i++))
    done

    python manage.py migrate
    python manage.py shell -c "from django.contrib.auth import get_user_model; User= get_user_model(); User.objects.create_superuser('$COLLAB_ADMIN_USER', '$COLLAB_ADMIN_EMAIL', '$COLLAB_ADMIN_PWD')"
    python manage.py loaddata $SRC/collab/data/perm.json

    echo "Ok" > $marker_file
fi

echo "$(basename $0) complete."
