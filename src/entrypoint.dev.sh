#!/bin/bash

pelican content \
    --output /dist \
    --settings pelicanconf.py \
    --extra-settings RELATIVE_URLS=true \
    --bind 0.0.0.0 \
    --port 8000 \
    --listen \
    --autoreload \
