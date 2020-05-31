SHELL:=/bin/bash

.PHONY: fmt
fmt:
	black .
	terraform fmt -recursive infra

.PHONY: lint
lint:
	flake8 browser tests

.PHONY: unit-test
unit-test:
	PYTHONWARNINGS=ignore:ResourceWarning python3 -m coverage run \
		--source=unit/backend \
		--omit=.coverage,venv,browser/backend/scripts/*,browser/backend/chalice/*,browser/backend/lambda/chalice/* \
		-m unittest discover \
		--start-directory tests/unit \
		--top-level-directory . \
		--verbose

.PHONY: functional-test
functional-test:
	python3 -m unittest discover --start-directory tests/functional --top-level-directory . --verbose
