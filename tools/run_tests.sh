#!/bin/bash
poetry install
pytest --no-xvfb tests/
