#!/bin/bash

# This script is based on the one you can find here: https://github.com/maoschanz/drawing
# (https://github.com/maoschanz/drawing/blob/master/utils-bash/deb_package.sh)

PACKAGE_NAME="pyopentracks"
VERSION="0.1.0"
#VERSION="$(git describe --tags --abbrev=0)"
#if [ $? != 0 ]
#then
#    echo "fatal: last version couldn't be got from git"
#    exit 1
#fi

function separator () {
	echo ""
	echo "---------------------------------------------------------------------"
	echo ""
}

echo "Package name: $PACKAGE_NAME"
echo "Package version: $VERSION"
echo ""
echo "Is it correct? [Return/^C]"
read confirmation
separator

# Remember current directory (theorically, the project's root) to bring the package here in the end
previous_dir=`pwd`

# Set up specific structure required by debian scripts
DIR_PATH=/tmp/building-dir
DIR_NAME=$PACKAGE_NAME'-'$VERSION
FILE_NAME=$PACKAGE_NAME'_'$VERSION

mkdir -p $DIR_PATH/$DIR_NAME/

cp -r build-aux $DIR_PATH/$DIR_NAME/
cp -r data $DIR_PATH/$DIR_NAME/
cp -r debian $DIR_PATH/$DIR_NAME/
cp -r po $DIR_PATH/$DIR_NAME/
cp -r pyopentracks $DIR_PATH/$DIR_NAME/
cp meson.build $DIR_PATH/$DIR_NAME/

cd $DIR_PATH/
tar -Jcvf $FILE_NAME.orig.tar.xz $DIR_NAME
cd $DIR_PATH/$DIR_NAME/
separator

# Automatic creation of additional files for the build process
dh_make -i -y
separator

# Actually building the package
dpkg-buildpackage -i -us -uc -b
separator

# Get the package in /tmp and move it where the user is
cp $DIR_PATH/*.deb $previous_dir

# Cleaning
ls $DIR_PATH
ls $DIR_PATH/$DIR_NAME
rm -r $DIR_PATH
cd $previous_dir
