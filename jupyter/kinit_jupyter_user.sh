#!/bin/bash

# Bootstrap example script
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# - The first parameter for the Bootstrap Script is the USER.
USER=$1
if [ "$USER" == "" ]; then #note the bash scripting condition has space around the logic
    echo $(date -u) "ErrNo1: No username was provided in \$USER." >> jupyterhub_event.log
    exit 2
elif [ "$USER" == "root" ]; then
    echo $(date -u) "ErrNo2: User root is not a valid user." >> jupyterhub_event.log
    exit 3
else
    # setup k5start
    k5pid=$(ps afxu | grep $USER.*k[5]start | awk '{ print $2 }')
    if [ ! -z $k5pid ]; then

        echo $(date -u) "Info1: k5start already running for $USER" >> /home/$USER/jupyterhub_event.log
        echo $(date -u) "Info1: SparkSession created for $USER." >> /home/$USER/jupyterhub_event.log

        exit 0
    else
        echo $(date -u) "Info2: starting k5start for $USER" >> /home/$USER/jupyterhub_event.log
    fi

    if [ -f /home/$USER/.$USER.keytab ] && [ -z $k5pid ]; then
        sudo -u $USER -- k5start -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f "/home/$USER/.$USER.keytab"
    elif [ -f /home/$USER/.keytab ] && [ -z $k5pid ]; then
        sudo -i $USER -- k5start -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f "/home/$USER/.keytab"
    else
        echo $(date -u) "Can't find a keytab for $USER." >> /home/$USER/jupyterhub_event.log
        exit 1
    fi

    exit 0
fi


#chmod 755 kinit_jupyter_user.sh
