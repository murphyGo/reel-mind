.PHONY: help install test test-unit test-property test-integration lint typecheck fmt web-install web-dev web-build web-lint web-typecheck clean

help:
	@echo "Python:"
	@echo "  install            Install Python deps with uv (runtime + dev)"
	@echo "  test               Run unit + property tests"
	@echo "  test-unit          Run unit tests only"
	@echo "  test-property      Run Hypothesis property tests only"
	@echo "  test-integration   Run integration tests (requires live creds)"
	@echo "  lint               ruff check"
	@echo "  typecheck          mypy"
	@echo "  fmt                ruff format"
	@echo "Web:"
	@echo "  web-install        Install Next.js deps with pnpm"
	@echo "  web-dev            Run Next.js dev server"
	@echo "  web-build          Build Next.js for production"
	@echo "  web-lint           ESLint"
	@echo "  web-typecheck      tsc --noEmit"

install:
	uv sync --all-extras

test:
	pytest -m "not integration"

test-unit:
	pytest tests/unit

test-property:
	pytest tests/property -m property

test-integration:
	pytest tests/integration -m integration

lint:
	ruff check .

typecheck:
	mypy src/

fmt:
	ruff format .
	ruff check --fix .

web-install:
	cd web && pnpm install

web-dev:
	cd web && pnpm dev

web-build:
	cd web && pnpm build

web-lint:
	cd web && pnpm lint

web-typecheck:
	cd web && pnpm exec tsc --noEmit

clean:
	rm -rf dist build .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf web/.next web/out
