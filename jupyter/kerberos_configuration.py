#Modify JupyterHub configuration
#At the end of jupyterhub-config.py, insert the following script:
from subprocess import check_call
import os
def my_kinit(spawner):
    username = spawner.user.name # get the username
    sudo='/bin/sudo/' #run the check_call with sudo
    script = '/usr/local/bin/kinit_jupyter_user.sh'
    check_call([sudo, script, username]) #running with sudo ensure accessible to log

# attach the hook function to the spawner
c.Spawner.pre_spawn_hook = my_kinit

