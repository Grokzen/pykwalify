help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean           remove temporary files created by build tools"
	@echo "  cleanall        all the above + tmp files from development tools"
	@echo "  cleanmeta       Cleans out all META.* files from the lib folder"
	@echo "  test            run test suite"
	@echo "  sdist           make a source distribution"
	@echo "  install         install package"

clean:
	-rm -f MANIFEST
	-rm -rf dist/*
	-rm -rf build/*

cleanmeta:
	-rm -rf lib/pykwalify/META-*

cleanall: clean cleanmeta
	-find . -type f -name "*~" -exec rm -f "{}" \;
	-find . -type f -name "*.orig" -exec rm -f "{}" \;
	-find . -type f -name "*.rej" -exec rm -f "{}" \;
	-find . -type f -name "*.pyc" -exec rm -f "{}" \;
	-find . -type f -name "*.parse-index" -exec rm -f "{}" \;

test:
	python runtests.py

sdist: cleanmeta
	python setup.py sdist

install: cleanmeta
	python setup.py install
