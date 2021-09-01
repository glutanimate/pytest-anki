SHELL = /bin/bash

PACKAGE = pytest_anki
TEST_FLAGS ?= -n4

# Set up project
install:
	poetry install

# Run tests
test:
	python -m pytest $(TEST_FLAGS) tests/

# Run type checkers
check:
	python -m mypy $(PACKAGE)

# Run code linters
lint:
	python -m flake8 $(PACKAGE)
	python -m black --check $(PACKAGE)

# Run code formatters
format:
	python -m isort $(PACKAGE)
	python -m black $(PACKAGE)

# Build project
build:
	poetry build

# Show help message
help:
	@echo "$$(tput bold)Available targets:$$(tput sgr0)";echo;sed -ne"/^# /{h;s/.*//;:d" -e"H;n;s/^# //;td" -e"s/:.*//;G;s/\\n# /---/;s/\\n/ /g;p;}" ${MAKEFILE_LIST}|LC_ALL='C' sort -f|awk -F --- -v n=$$(tput cols) -v i=19 -v a="$$(tput setaf 6)" -v z="$$(tput sgr0)" '{printf"%s%*s%s ",a,-i,$$1,z;m=split($$2,w," ");l=n-i;for(j=1;j<=m;j++){l-=length(w[j])+1;if(l<= 0){l=n-i-length(w[j])-1;printf"\n%*s ",-i," ";}printf"%s ",w[j];}printf"\n";}'

.DEFAULT_GOAL: help
.PHONY: install test build check lint format
