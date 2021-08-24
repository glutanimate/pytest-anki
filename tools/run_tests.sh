#!/bin/bash
poetry install
pytest -n4 tests/
