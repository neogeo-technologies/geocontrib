#!/bin/bash
# --------------------------------------------------------------- #
# Variable

# --------------------------------------------------------------- #
# Fonction
statusExit()
{
    if [ $? -eq 0 ]
    then
        echo -e "\n[  OK  ]  $1"
        echo "# --------------------------------------------------------------- #"
    else
        echo -e "\n[FAILED]  $1 \n"
        exit 1
    fi
}
# --------------------------------------------------------------- #

# --------------------------------------------------------------- #
# Main

# Execution des scripts du répertoire ./scripts/
cd $APP_PATH
for entry in ./$SRC/docker_data/scripts/*.sh
do
    $entry
    statusExit "$entry"
done
