#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TOP_LEVEL="${SCRIPT_DIR}/.."

${TOP_LEVEL}/main-env/bin/python3 ${TOP_LEVEL}/main.py
