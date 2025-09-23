#!/usr/bin/env bash

exec \
    /usr/local/bin/python /app/Mylar.py \
        --nolaunch \
        --quiet \
        --datadir /config/mylar
