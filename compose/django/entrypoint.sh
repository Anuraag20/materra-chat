#!/bin/bash

python3 manage.py migrate
mkdir media/
python3 manage.py runserver 0.0.0.0:80
