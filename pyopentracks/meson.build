pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name(), 'data')
moduledir = join_paths(pkgdatadir, 'pyopentracks')

python = import('python')

conf = configuration_data()
conf.set('APP_ID', application_id)
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'pyopentracks.py.in',
  output: 'pyopentracks',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

configure_file(
  input: 'settings.py.in',
  output: 'settings.py',
  configuration: conf,
  install: true,
  install_dir: moduledir
)

# pyopentracks_sources = [
#   '__init__.py',
#   'main.py',
#   'app.py',
#   'app_window.py',
#   'file_chooser.py',
#   'gpx_parser.py',
#   'track_stats.py',
#   'layout.py',
#   'utils.py',
#   'maps.py',
# ]

#install_data(pyopentracks_sources, install_dir: moduledir)

install_subdir(
  '.',
  install_dir: moduledir
)
