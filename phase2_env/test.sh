#!/usr/bin/env bash
python build_env.py -b . -o /tmp/config.json

python monitor_train.py -c /tmp/config.json -t example_train.hdf

PYTHONPATH=$(realpath ..) python monitor_test.py -c /tmp/config.json -g example_ground_truth.hdf
