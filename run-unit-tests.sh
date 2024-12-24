#!/bin/bash

set -e  # Exit immediately if any command fails

export PYTHONPATH=$PYTHONPATH:$(pwd)
export SERVICE_DATA_PATH=$(pwd)/service_data
export COPILOT_LOG_LEVEL=INFO
export COPILOT_LOG_PATH=$SERVICE_DATA_PATH/logs/

python opencopilot/tests/unit_tests/test_json_block_extractor.py