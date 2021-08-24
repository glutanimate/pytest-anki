#!/bin/bash
poetry install
python -m pytest -n4 tests/
