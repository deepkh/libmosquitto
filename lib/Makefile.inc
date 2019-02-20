# Copyright (c) 2018, Gary Huang, deepkh@gmail.com, https://github.com/deepkh
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

SHELL=/bin/sh

LIBMOSQUITTO: ${LIBMOSQUITTO_DLL}
	@echo MAKE $@ 

LIBMOSQUITTO_CLEAN: ${LIBMOSQUITTO_DLL_CLEAN}
	@echo MAKE $@ 

# due to lib and src use same code directly, so need to clean lib before make src
${LIBMOSQUITTO_DLL}:
	$(CD) ${LIBMOSQUITTO} && $(MAKE) -f Makefile.${LIBMOSQUITTO_NAME} ${LIBMOSQUITTO_DLL_CLEAN}
	$(CD) ${LIBMOSQUITTO} && $(MAKE) -f Makefile.${LIBMOSQUITTO_NAME} -j8 $@

LIBMOSQUITTO_DEV: 
	$(CD) ${LIBMOSQUITTO} && $(MAKE) -f Makefile.${LIBMOSQUITTO_NAME} ${LIBMOSQUITTO_DLL}
	@echo MAKE $@ 

${LIBMOSQUITTO_DLL_CLEAN}:
	$(CD) ${LIBMOSQUITTO} && $(MAKE) -f Makefile.${LIBMOSQUITTO_NAME} $@

