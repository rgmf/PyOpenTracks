# Install Dependencies
In Debian:

sudo apt install libgtk-3-dev

sudo apt install libchamplain-gtk-0.12-dev

sudo apt install libchamplain-0.12-dev

sudo apt install libcairo2-dev

sudo apt install libgirepository1.0-dev

sudo apt install python3-numpy

sudo apt install python3-matplotlib

sudo apt install meson ninja-build

sudo apt install appstream-util

sudo apt install gettext

# Virtual Environment
pipenv --three

pipenv shell

pipenv install

# Build
`sh build.sh`

# Execute
After building enter to `buildir/buildir/testdir/bin` and execute `./pyopentracks`.

# Internacionalization (i10n)
Enter to `po/` directory and execute `update_potfiles.sh` to create a new language PO file or update the string to a language. Then edit the PO file and execute `compile_potfiles.sh` to generate mo file.

# Flatpak
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
