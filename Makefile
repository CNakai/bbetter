.PHONY: dist dev

dist:
	python3 setup.py sdist bdist_wheel

dev:
	pip install --editable .
