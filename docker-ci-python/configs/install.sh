#!/bin/sh
REQS=$(python /build/configs/setup.py list-requirements)
if [ -n "$REQS" ]; then
    pip install -q $REQS
fi
