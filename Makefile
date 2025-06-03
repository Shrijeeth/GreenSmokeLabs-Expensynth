install-backend:
	cd backend && python -m pip install .

install-backend-dev:
	cd backend && python -m pip install .[dev]

format-backend:
	cd backend && python -m ruff format .

lint-backend:
	cd backend && python -m ruff check --select I,RUF022 --fix .

check-backend:
	cd backend && python -m ruff check .

deploy-backend-dev:
	cd backend && modal deploy green_smoke_labs_expensynth/main.py --env dev

deploy-backend-prod:
	cd backend && modal deploy green_smoke_labs_expensynth/main.py --env prod