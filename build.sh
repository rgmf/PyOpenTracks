#!/bin/sh

pwd
rm -rf buildir
mkdir buildir
cd buildir
meson ..
meson configure -Dprefix=$PWD/buildir/testdir
ninja
ninja install
