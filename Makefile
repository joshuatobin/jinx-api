#!/usr/bin/make -f

SRCDIR=src

all:
# Add commands here to build code.

install:

install:
	install -m 755 -o root -g root -d ${DESTDIR}/var/www/jinx_api
	cp -r $(SRCDIR)/jinx_api/* $(DESTDIR)/var/www/jinx_api/

clean:

deb:
	debuild -uc -us -b
debclean:
	debuild clean

