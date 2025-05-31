.PHONY: lint add-%

add-%:
	pip install $* && pip freeze > requirements.txt

lint:
	black .
	isort .
	python -m autoflake --in-place --remove-all-unused-imports --recursive .
	mypy . 
	pylint **/*.py

