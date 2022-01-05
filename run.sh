#!/bin/sh

# GSETTINGS_SCHEMA_DIR=buildir/buildir/testdir/share/glib-2.0/schemas/
# XDG_DATA_HOME=xdg_data_home/local/share/
# XDG_CONFIG_HOME=xdg_data_home/config/
# XDG_STATE_HOME=xdg_data_home/local/state/
# XDG_STATE_HOME=xdg_data_home/local/bin/
# XDG_DATA_DIRS=xdg_data_home/usr/local/share
# XDG_CONFIG_DIRS=xdg_data_home/etc/xdg/
# XDG_CACHE_HOME=xdg_data_home/cache/
# XDG_RUNTIME_DIR=xdg_data_home/runtime/dir/


GSETTINGS_SCHEMA_DIR=buildir/buildir/testdir/share/glib-2.0/schemas/ \
XDG_DATA_HOME=xdg_data_home/local/share/ \
XDG_CONFIG_HOME=xdg_data_home/config/ \
XDG_RUNTIME_DIR=xdg_data_home/runtime/dir/ \
XDG_CONFIG_DIRS=xdg_data_home/etc/xdg/ \
XDG_CACHE_HOME=xdg_data_home/cache/ \
./buildir/buildir/testdir/bin/pyopentracks --loglevel 1
