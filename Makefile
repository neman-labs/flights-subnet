VENV=.venv

ACTIVATE_SCRIPT := $(VENV)/bin/activate
ACTIVATE_VENV := . $(ACTIVATE_SCRIPT) \
@echo "Using virtual env: ${VENV}"

$(VENV):
	$(info Creating virtual env: $(VENV))
	python3.10 -m venv $(VENV)

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: sync
sync: $(VENV) ## Setup virtual environment and run sync
	$(ACTIVATE_VENV) && $(VENV)/bin/pip install --upgrade pip && \
	$(VENV)/bin/pip install -r requirements.txt --no-cache ;

.PHONY: format
format: ## Run all formatting checks
	$(ACTIVATE_VENV) && $(VENV)/bin/ruff format ;

.PHONY: lint
lint:  ## Run all linting checks
	$(ACTIVATE_VENV) && $(VENV)/bin/ruff check ;

.PHONY: lint-fix
lint-fix:  ## Run all linting checks with auto-fix
	$(ACTIVATE_VENV) && $(VENV)/bin/ruff check --fix ;

.PHONY: build-validator-environment  ## Build the validator environment
build-validator-environment:
	docker-compose --env-file validator.env build

.PHONY: run-validator-environment  ## Run the validator environment
run-validator-environment:
	docker-compose --env-file validator.env up -d

.PHONY: run-validator
run-validator:  ## Run the validator
	bash scripts/start_validator.sh

.PHONY: run-miner
run-miner:  ## Run the miner
	bash scripts/start_miner.sh
