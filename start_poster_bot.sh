#!/bin/bash
source /root/PosterBot/myenv/bin/activate
nohup python3 /root/PosterBot/main.py > /dev/null 2>&1 &
