VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
FLAKE8 = $(VENV)/bin/flake8
MYPY = $(VENV)/bin/mypy
EXCLUDE = venv,__pycache__,.mypy_cache

MAIN = main.py
CONFIG = config.txt

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

lint:
	$(FLAKE8) . --exclude=$(EXCLUDE)
	$(MYPY) . --exclude=$(EXCLUDE) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(FLAKE8) . --exclude=$(EXCLUDE)
	$(MYPY) . --exclude=$(EXCLUDE)--strict
