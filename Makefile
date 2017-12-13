help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean           remove temporary files created by build tools"
	@echo "  cleanegg        remove temporary files created by build tools"
	@echo "  cleanpy         remove temporary python files"
	@echo "  cleancov        remove files used and generated by coverage tools"
	@echo "  cleanall        all the above + tmp files from development tools (Not cleantox)"
	@echo "  cleantox        remove files created by tox"
	@echo "  test            run test suite"
	@echo "  sdist           make a source distribution"
	@echo "  install         install package"

clean:
	-rm -f MANIFEST
	-rm -rf dist/
	-rm -rf build/

cleantox:
	-rm -rf .tox/

cleancov:
	coverage combine
	coverage erase
	-rm -rf htmlcov/

cleanegg:
	-rm -rf pykwalify.egg-info/

cleanpy:
	-find . -type f -name "*~" -exec rm -f "{}" \;
	-find . -type f -name "*.orig" -exec rm -f "{}" \;
	-find . -type f -name "*.rej" -exec rm -f "{}" \;
	-find . -type f -name "*.pyc" -exec rm -f "{}" \;
	-find . -type f -name "*.parse-index" -exec rm -f "{}" \;
	-find . -type d -name "__pycache__" -exec rm -rf "{}" \;

cleanall: clean cleanegg cleanpy cleancov

test:
	coverage erase
	coverage run --source pykwalify/ -m pytest
	coverage report -m

sdist:
	python setup.py sdist

install:
	python setup.py install
