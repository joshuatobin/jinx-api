#!/usr/bin/make -f

SRCDIR=src

all:
# Add commands here to build code.

install:
	hg --config 'ui.verbose=False' manifest | grep '^$(SRCDIR)/' | cut -f 2- -d '/' | \
		while read file; do \
			# create containing directory \
			install -v -m 755 -o root -g root -d "$$(dirname "$(DESTDIR)/$$file")"; \
			if [ -x "$(SRCDIR)/$$file" ]; then \
				install -v -m 755 -o root -g root "$(SRCDIR)/$$file" "$(DESTDIR)/$$file"; \
			else \
				install -v -m 644 -o root -g root "$(SRCDIR)/$$file" "$(DESTDIR)/$$file"; \
			fi; \
		done

# Add commands here to set special permissions, owners, and groups.
# Example:
#
#	chmod u+s $(DESTDIR)/usr/bin/sudo

clean:
		
deb:
	debuild -uc -us -b
	
debclean:
	debuild clean
	

