all: test mypy black

.PHONY: test
test:
	pytest

.PHONY: coverage
coverage:
	pytest --cov src/ofxstatement_otp

.PHONY: black
black:
	black setup.py src tests

.PHONY: mypy
mypy:
	mypy src tests
