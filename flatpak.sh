export CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
flatpak-builder --force-clean --user --install flatpakdir es.rgmf.pyopentracks.json
if [ $? -eq 0 ];
then
    flatpak run es.rgmf.pyopentracks.dev
fi
