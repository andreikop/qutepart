VERSION=$(shell ./setup.py --version)
AUTHOR=$(shell ./setup.py --author)
AUTHOR_EMAIL=$(shell ./setup.py --author-email)
PACKAGE_NAME=$(shell ./setup.py --name)
DEB_PACKAGE_NAME=python3-$(PACKAGE_NAME)
ARCHIVE=$(PACKAGE_NAME)-$(VERSION).tar.gz

ENV=DEBFULLNAME="$(AUTHOR)" DEBEMAIL=$(AUTHOR_EMAIL) EDITOR=enki

DEBIGAN_ORIG_ARCHIVE=${DEB_PACKAGE_NAME}_${VERSION}.orig.tar.gz

DEB_BUILD_DIR=build/deb
OBS_REPO=home:hlamer:enki
OBS_REPO_DIR=build/obs_home_hlamer_enki


all install:
	@echo This Makefile does not build and install the project.
	@echo Use setup.py script
	@exit 1

bump-version:
	enki-ng qutepart/version.py
	enki-ng rpm/python3-qutepart.spec +2

changelog-update:
	enki-ng ChangeLog
	cd debian && \
		$(ENV) dch --check-dirname-regex qutepart -v $(VERSION)-1~ubuntuseries1 -b --distribution ubuntuseries
	enki-ng rpm/python3-qutepart.spec +60

dist/${ARCHIVE}:
	rm -rf dist
	./setup.py sdist


deb-obs: dist/${ARCHIVE}
	rm -rf ${DEB_BUILD_DIR}
	mkdir ${DEB_BUILD_DIR}
	cp dist/${ARCHIVE} ${DEB_BUILD_DIR}/${DEBIGAN_ORIG_ARCHIVE}
	cd ${DEB_BUILD_DIR} && tar -xf ${DEBIGAN_ORIG_ARCHIVE}
	cp -r debian ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION}
	sed -i s/ubuntuseries/obs/g ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/debian/changelog
	cd ${DEB_BUILD_DIR}/${PACKAGE_NAME}-${VERSION} && $(ENV) debuild -us -uc -S

${OBS_REPO_DIR}:
	mkdir -p build
	osc co $(OBS_REPO) python3-qutepart
	mv $(OBS_REPO) ${OBS_REPO_DIR}

put-obs: ${OBS_REPO_DIR} deb-obs
	rm -f ${OBS_REPO_DIR}/python3-qutepart/*
	cp rpm/python3-qutepart.spec ${OBS_REPO_DIR}/python3-qutepart
	cp dist/${ARCHIVE} ${OBS_REPO_DIR}/python3-qutepart
	cp ${DEB_BUILD_DIR}/*.debian.tar.xz ${OBS_REPO_DIR}/python3-qutepart
	cp ${DEB_BUILD_DIR}/*.orig.tar.gz ${OBS_REPO_DIR}/python3-qutepart
	cp ${DEB_BUILD_DIR}/*.dsc ${OBS_REPO_DIR}/python3-qutepart
	cd ${OBS_REPO_DIR}/python3-qutepart && \
		osc addremove && \
		osc ci -m 'update by the publish script'

sdist:
	./setup.py sdist --formats=gztar,zip

wheels:
	-rm dist/*.whl
	./setup.py bdist_wheel --skip-extension

push-wheels-to-test:
	 python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*.tar.gz dist/*.whl

help:
	@echo 'bump-version                Open version file to edit'
	@echo 'changelog-update            Update Debian and RedHat changelogs'
	@echo 'put-obs                     Upload version to OBS'
	@echo 'sdist                       Make source distribution'
