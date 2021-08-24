#!/bin/bash
poetry install
export QT_DEBUG_PLUGINS=1
QT_DEBUG_PLUGINS=1 pytest tests/
