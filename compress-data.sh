#!/usr/bin/env bash
tar -I "zstd -T36 -19" --checkpoint=.1024 --totals -c -f data-p3.tar.zst Data fig old P3-Replication-1.0-SNAPSHOT-all.jar utils.py
