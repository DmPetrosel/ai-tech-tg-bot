# include .BaseBot.env
# export
run_bot:
	@echo "Launching Telegram-bot"
	. ./.venv/bin/activate && python3 main.py

# run_bot:
# 	@echo "Launching Telegram-bot"
# 	. ./.venv/bin/activate && cd ./src/ && python3 main.py
run_dev:
	@echo "Launching Telegram-bot"
	 cd ./src/ && python3 main.py

install:
	python3.11 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
# . .venv/bin/activate && cd ./src/ && mkdir -p alembic/versions/ && alembic revision --autogenerate -m 'init' && alembic upgrade head

install_dev:
	pip install -e .[dev,test] -U

uninstall:
	rm -rf .venv
	rm -rf src/alembic/versions/
	rm -rf src/database.db
update:
	. .venv/bin/activate && pip install -r requirements.txt

lint:
	ruff check .
	ruff format . --check

format:
	ruff check . --fix
	ruff format .

run_alembic:
	. .venv/bin/activate && cd ./src/ && mkdir -p alembic/versions/ && alembic revision --autogenerate -m '$(comment)' && alembic upgrade head

clean:
	rm -rf src/*.egg-info *.egg_info __pycache__ build/