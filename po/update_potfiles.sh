#!/bin/bash

SRCDIR="pyopentracks"
DATADIR="data"
APPNAME="es.rgmf.pyopentracks"

if [ -z $1 ]; then
    echo "Usage: $0 lang"
    exit
fi
lang="$1"

rm *.pot

version=$(fgrep -m 1 "version: " ../meson.build | grep -v "meson" | grep -o "'.*'" | sed "s/'//g")

echo "# Auto-generated by update_potfiles.sh" > POTFILES
for filename in `find ../$SRCDIR -iname "*.py"`
do
    echo $filename | sed "s/\.\.\///" >> POTFILES
done

find ../$SRCDIR -iname "*.py" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-python.pot
find ../$DATADIR/ui -iname "*.ui" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-ui.pot -L Glade

msgcat --use-first $APPNAME-python.pot $APPNAME-ui.pot > $APPNAME.pot

[ -f "${lang}.po" ] && mv "${lang}.po" "${lang}.po.old"
msginit --locale=$lang --input $APPNAME.pot
if [ -f "${lang}.po.old" ]; then
    mv "${lang}.po" "${lang}.po.new"
    msgmerge -N "${lang}.po.old" "${lang}.po.new" > ${lang}.po
    rm "${lang}.po.old" "${lang}.po.new"
fi
sed -i 's/ASCII/UTF-8/' "${lang}.po"
rm *.pot
