VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)
PACKAGE_NAME=$(shell ./setup.py --name)
DEB_PACKAGE_NAME=python-$(PACKAGE_NAME)
ARCHIVE=$(PACKAGE_NAME)-$(VERSION).tar.gz

ENV=DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) EDITOR=enki

DEBIGAN_ORIG_ARCHIVE=${DEB_PACKAGE_NAME}_${VERSION}.orig.tar.gz


all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit -1

bump-version:
	enki qutepart/__init__.py +29
	enki rpm/python-qutepart.spec +2

changelog-update:
	enki ChangeLog
	cd debian && \
		$(ENV) dch --check-dirname-regex qutepart -v $(VERSION)-1~ubuntuseries1 -b --distribution ubuntuseries
	enki rpm/python-qutepart.spec +60

dist/${ARCHIVE}:
	rm -rf dist
	./setup.py sdist


deb-obs: dist/${ARCHIVE}
	rm -rf build-obs
	mkdir build-obs
	cp dist/${ARCHIVE} build-obs/${DEBIGAN_ORIG_ARCHIVE}
	cd build-obs && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian build-obs/${PACKAGE_NAME}-${VERSION}
	sed -i s/ubuntuseries/obs/g build-obs/${PACKAGE_NAME}-${VERSION}/debian/changelog
	cd build-obs/${PACKAGE_NAME}-${VERSION} && $(ENV) debuild -us -uc -S

obs_home_hlamer_enki:
	osc co home:hlamer:enki python-qutepart
	mv home\:hlamer\:enki obs_home_hlamer_enki

put-obs: obs_home_hlamer_enki deb-obs
	rm -f obs_home_hlamer_enki/python-qutepart/*
	cp rpm/python-qutepart.spec obs_home_hlamer_enki/python-qutepart
	cp dist/${ARCHIVE} obs_home_hlamer_enki/python-qutepart
	cp build-obs/*.debian.tar.gz obs_home_hlamer_enki/python-qutepart
	cp build-obs/*.orig.tar.gz obs_home_hlamer_enki/python-qutepart
	cp build-obs/*.dsc obs_home_hlamer_enki/python-qutepart
	cd obs_home_hlamer_enki/python-qutepart && \
		osc addremove && \
		osc ci -m 'update by the publish script'

sdist:
	./setup.py sdist --formats=gztar,zip

help:
	@echo 'bump-version                Open version file to edit'
	@echo 'changelog-update            Update Debian and RedHat changelogs'
	@echo 'put-obs                     Upload version to OBS'
	@echo 'sdist                       Make source distribution'
