#!/bin/bash

source env_exports.sh
CROSS_COMPILE=x86_64-w64-mingw32-

targets=(lib src client)

build() {
	for i in "${targets[@]}"
	do
		CROSS_COMPILE=${CROSS_COMPILE} make -C $i $1 -j8
	done
}

all() {
	build all
}

clean() {
	build clean
}
$@
