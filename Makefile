SHELL:=/bin/bash

.PHONY: fmt
fmt:
	black .

.PHONY: lint
lint:
	flake8 backend tests

.PHONY: unit-test
unit-test:
	-docker run -d -p 5432:5432 --name test_db -e POSTGRES_PASSWORD=test_pw postgres
	PYTHONWARNINGS=ignore:ResourceWarning python3 -m coverage run \
		-m unittest discover --start-directory tests/unit/backend --top-level-directory . --verbose; \
	test_result=$$?; \
	$(MAKE) clean_test_db; \
	exit $$test_result


clean_test_db:
	-docker stop test_db
	-docker rm test_db

.PHONY: functional-test
functional-test:
	python3 -m unittest discover --start-directory tests/functional --top-level-directory . --verbose

.PHONY: local-database
local-database: clean_test_db
	docker run -d -p 5432:5432 --name test_db -e POSTGRES_PASSWORD=test_pw postgres
	python3 ./scripts/populate_db.py


.PHONY: local-backend
local-backend:
	$(MAKE) local-server -C ./backend/chalice/api_server

.PHONY: smoke-test-prod-build
smoke-test-prod-build:
	$(MAKE) smoke-test-prod-build -C ./frontend

.PHONY: smoke-test-with-local-backend
smoke-test-with-local-backend:
	$(MAKE) smoke-test-with-local-backend -C ./frontend

.PHONY: smoke-test-with-local-backend-ci
smoke-test-with-local-backend-ci:
	$(MAKE) smoke-test-with-local-backend-ci -C ./frontend
