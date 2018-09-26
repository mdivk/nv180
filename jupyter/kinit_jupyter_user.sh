#!/bin/bash

# Bootstrap example script
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# - The first parameter for the Bootstrap Script is the USER.
USER=$1
if [ "$USER" == "" ]; then #note the bash scripting condition has space around the logic
    exit 1
elif [ "$USER" == "root" ]	
	exit 0
then
	k5start -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f "/home/$USER/.$USER.keytab"
	exit 0
fi

#chmod 755 kinit_jupyter_user.sh
