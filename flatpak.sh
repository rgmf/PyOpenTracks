rm -rf .pyopentracks-dev 2> /dev/null
mkdir .pyopentracks-dev
cp -r build-aux data po pyopentracks tests es.rgmf.pyopentracks-dev.json meson.build .pyopentracks-dev/.
flatpak-builder --force-clean --user --install flatpakdir es.rgmf.pyopentracks-dev.json
flatpak run --socket=session-bus es.rgmf.pyopentracks-dev
