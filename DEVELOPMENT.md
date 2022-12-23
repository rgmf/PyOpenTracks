# Install Dependencies
In Debian:

sudo apt install libgtk-3-dev libchamplain-gtk-0.12-dev libchamplain-0.12-dev libcairo2-dev libgirepository1.0-dev python3-numpy python3-matplotlib meson ninja-build appstream-util gettext

# Build
`sh build.sh`

# Execute
After building enter to `buildir/buildir/testdir/bin` and execute `./pyopentracks`.

`./pyopentracks` can receive command line arguments:
- `--loglevel` to indicate log level with an integer value from 1 to 5 (DEBUG, INFO, WARNING, ERROR, CRITICAL).

Also, you can run the shell script `sh run.sh` after building the project with `sh build.sh`. This `run.sh` script pass to `./pyopentracks` a set of environment variables and use `--loglevel` argument with a value of `3` that you can change.

# Tests
There are tests in the `tests` folder. To execute them, run the following command from project root directory:

`python3 -m unittest discover -v -s tests/`

To run a single test, for example the test_fit_parser.py tests:

`python3 -m unittest tests.test_fit_parser`

You have to make sure that `python3-mock` is installed to run tests.

Also, you should execute `sh build.sh` if there are changes before lauch tests.

# Logs
PyOpenTracks uses `logging` standard Python library for logs. You can set the log's level executing PyOpenTracks from terminal and passing to it the argument `--loglevel` with a value:
- 1: DEBUG, INFO, WARNING, ERROR and CRITICAL logs.
- 2: INFO, WARNING, ERROR and CRITICAL logs.
- 3: WARNING, ERROR and CRITICAL logs.
- 4: ERROR and CRITICAL logs.
- 5: CRITICAL logs.

You can see logs from console when you execute PyOpenTracks from terminal or in the journald systemd (/var/log/messages typically on Debian).

# Internacionalization (i10n)
Enter to `po/` directory and execute `update_potfiles.sh` to create a new language PO file or update the string to a language. Then edit the PO file and execute `compile_potfiles.sh` to generate mo file.

# Debian
Execute `deb_package.sh` to build a .deb package that you can install on Debian distributions.

If you install PyOpenTracks by installing .deb package then you have to be careful because gsettings to be used are the same than developing execution (see data/es.rgmf.pyopentracks.gschema.xml where is specified the path of the settings that you can see through dconf-editor, for example).

You can install PyOpenTracks through the deb package and test developing version (building and running the deveoping version) but this one need a change so both not use the same gsettings: change `path` attribute from `schema` tag on `data/es.rgmf.pyopentracks.gschema.xml`. Before pushing changes you has to restore this change.

# Flatpak
There are two JSON manifests:

- es.rgmf.pyopentracks.json
- es.rgmf.pyopentracks-dev.json

You should use the second one to development and the first one to send it to production.

If you want to use flatpak to test your changes all you have to do is execute the `flatpak.sh` script.

## Pre
You need to install `flatpak` and `flatpak-builder` from your distro repositories or whatever you want.

Then, you maybe want to add the Flathub repository:
`flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo`

And then, you'll need execute the following:

`flatpak install flathub org.gnome.Sdk//master`

`flatpak install flathub org.gnome.Platform//master`


## Build
You can execute the following command indicating the folder where you want to build PyOpenTracks using flatpak:

`flatpak-builder <flatpak build directory> es.rgmf.pyopentracks.json`

Also, if you want to re-build and clean all:

`flatpak-builder --force-clean <flatpak build directory> es.rgmf.pyopentracks.json`

And, finally if you want to get verbose information about the build process use the option `-v`.

## Build and install locally
You can build and install locally at the same time with the following command:

`flatpak-builder --user --install <flatpak build directory> es.rgmf.pyopentracks.json`

## Execute the locally installation
`flatpak run es.rgmf.pyopentracks`

If you get an error like this: 

"Failed to register: GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown: org.freedesktop.DBus.Error.ServiceUnknown"

Then, execute the command like this:

`flatpak run --socket=session-bus es.rgmf.pyopentracks`

## Settings values on Flatpak environment
After install PyOpenTracks through Flatpak, the settings values in the following file:

`~/.var/app/es.rgmf.pyopentracks/config/glib-2.0/settings/keyfile`

## PyOpenTracks data on Flatpak environment
After install PyOpenTracks through Flatpak, the database and local app data are in the following folder:

`~/.var/app/es.rgmf.pyopentracks/data/PyOpenTracks/`

# Icons
If you want or need to add icons you can do it using these two resources:
- https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
- Icon Library: https://gitlab.gnome.org/World/design/icon-library

