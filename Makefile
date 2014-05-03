PYTHON=$(shell which python)
PIP=$(shell which pip)
.PHONY: clean doc remote_doc test develop

develop:
	$(PYTHON) setup.py develop

doc:
	(cd doc; make html)

remote_doc:
	curl -X POST http://readthedocs.org/build/rdccommon

clean:
	find . -name \*.pyc | xargs rm -f
	(cd doc; rm -rf _build/*)

test:
	$(PIP) install -r requirements-dev.txt
	nosetests --with-doctest --with-coverage
