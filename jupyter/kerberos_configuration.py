#Modify JupyterHub configuration
#At the end of jupyterhub-config.py, insert the following script:
from subprocess import check_call
import os
def my_kinit(spawner):
    username = spawner.user.name # get the username
    script = '/usr/bin/kinit_jupyter_user.sh'
    check_call([script, username])

# attach the hook function to the spawner
c.Spawner.pre_spawn_hook = my_kinit
