PYTHON=$(shell which python)
PIP=$(shell which pip)
.PHONY: clean doc remote_doc test develop

install:
	$(PIP) install .

install-dev:
	$(PYTHON) setup.py develop
	$(PIP) install -r requirements-dev.txt

doc: clean install-dev
	(cd doc; make html)

remote_doc:
	curl -X POST http://readthedocs.org/build/rdcdic

clean:
	find . -name \*.pyc | xargs rm -f
	(cd doc; rm -rf _build/*)

test: clean install-dev
	$(PIP) install -r requirements-dev.txt
	nosetests -q --with-doctest --with-coverage --cover-package=rdc.dic
