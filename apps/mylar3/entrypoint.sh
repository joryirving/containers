#!/usr/bin/env bash

exec \
    python3 /app/mylar/Mylar.py \
        --nolaunch \
        --quiet \
        --datadir /config/mylar
