#!/bin/bash

#TO START APP WITH ANACONDA
source /home/candra/anaconda3/etc/profile.d/conda.sh
conda activate flaskmvc
uwsgi /mnt/f/PythonProjects/FLASKMVC/flask-mvc/site.ini # > /dev/null 2>&1
conda deactivate
