#!/bin/sh

set -e

USER_UID=$(stat -c '%u' /project)
USER_GID=$(stat -c '%g' /project)

UR=jupyter
HM=/home/jupyter

groupadd --gid $USER_GID $UR
useradd -d $HM -s /bin/sh -d $HM --uid $USER_UID --gid $USER_GID $UR

chown -R $UR:$UR $HM

if [[ "$1" == ssh ]]; then
  /bin/sh
else
  su $UR -c "/usr/local/bin/jupyter-notebook --config=/config.py"
fi
