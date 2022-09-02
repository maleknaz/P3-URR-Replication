#!/usr/bin/env bash
tar -I "zstd -T36 -19" --checkpoint=.1024 --totals -c -f data-p3.tar.zst ./*
