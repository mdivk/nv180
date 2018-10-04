#!/bin/bash

# Bootstrap example script
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# - The first parameter for the Bootstrap Script is the USER.
USER=$1
if [ "$USER" == "" ]; then #note the bash scripting condition has space around the logic
    echo "No username was provided in \$USER." > jupyterhub_error.log
    exit 2
elif [ "$USER" == "root" ]; then
    echo "User root is not a valid user." > jupyterhub_error.log
    exit 3
else
    if [ -f /home/$USER/$USER.keytab ]; then
        k5start -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f "/home/$USER/.$USER.keytab"
    elif [ -f /home/$USER/.keytab ]; then
        k5start -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f "/home/$USER/.keytab"
    else
        echo "Can't find a keytab for $USER." > /home/$USER/jupyterhub_error.log
        exit 1
    fi
    exit 0
fi
