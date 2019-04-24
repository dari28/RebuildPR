#!/bin/bash
pwd > /home/vnc/file
cd /home/vnc/Desktop/RebuildPR/code
/usr/bin/python manage.py runserver 0.0.0.0:8000
