#!/bin/sh

set -e

USER_UID=$(stat -c '%u' /project)
USER_GID=$(stat -c '%g' /project)

USER=jupyter
HOME=/home/jupyter

mkdir $HOME

groupadd --gid $USER_GID $USER
useradd -d $HOME --uid $USER_UID --gid $USER_GID $USER
chown $USER:$USER $HOME

if [[ "$1" == ssh ]]; then
  /bin/sh
else
  su -s /bin/sh $USER -c "/usr/local/bin/jupyter-notebook --config=config.py"
fi