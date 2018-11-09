#!/bin/bash

USER=$1
echo $(date) "InfoNo1: current user: $USER." >>  /home/$USER/jupyterhub_event.log
echo $(date) "InfoNo1: Starting ticket granting process......." >>  /home/$USER/jupyterhub_event.log

if [ "$USER" == "" ]; then #note the bash scripting condition has space around the logic
    echo $(date) "ErrNo1: No username was provided in \$USER." >>  /home/$USER/jupyterhub_event.log
    exit 2
elif [ "$USER" == "root" ]; then
    echo $(date) "ErrNo2: User root is not a valid user." >>  /home/$USER/jupyterhub_event.log
    exit 3
elif [ -z /home/$USER/.*keytab ]; then
    echo $(date) "ErrNo4: Can't find a keytab for $USER. Using genkt.py -u <userid> to generate keytab first" >> /home/$USER/jupyterhub_event.log
    exit 1
fi

# setup k5start
k5pid=$(ps afxu | grep $USER.*k[5]start | awk '{ print $2 }')

echo $(date) "InfoNo2: k5pid is: $k5pid"  >> /home/$USER/jupyterhub_event.log

# check here if k5start is already running, if yes, proceed to ticket issuing logic
# if not, k5start must be started first

if [ -z "$k5pid" ]; then
    sudo -u $USER -- k5start -v -b -K 300 -l 14d -f /home/$USER/.*keytab
    echo $(date) "WarnNo3: k5pid was not found, starting now" >> /home/$USER/jupyterhub_event.log
else
    # Now that a pid is created, proceed with the ticket granting/renewing with the user's keytab
    echo $(date) "InfoNo3: Current k5pid: $k5pid"  >> /home/$USER/jupyterhub_event.log
    echo $(date) "InfoNo3: Initiating Kerberos ticket granting" >> /home/$USER/jupyterhub_event.log
    sudo -u $USER -- k5start -v -b -K 300 -l 14d -p "/home/$USER/.k5start.pid" -f /home/$USER/.*keytab >> /home/$USER/jupyterhub_event.log
fi

exit 0
