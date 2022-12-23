project('pyopentracks',  
          version: '0.1.0',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')

application_id = 'es.rgmf.pyopentracks'

if get_option('profile') == 'development'
	application_id = 'es.rgmf.pyopentracks.dev'
endif

subdir('data')
subdir('pyopentracks')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
