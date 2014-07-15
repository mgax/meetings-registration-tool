from flask.ext.assets import Environment, Bundle


_BUNDLE_CSS = (
    'css/bootstrap.min.css',
    'css/bootstrap-theme.min.css',
    'css/main.css',
)


_BUNDLE_JS = (
    'js/lib/jquery.min.js',
    'js/lib/bootstrap.min.js',
)


css = Bundle(*_BUNDLE_CSS, filters='cssmin', output='gen/static.css')
js = Bundle(*_BUNDLE_JS, filters='jsmin', output='gen/static.js')


assets_env = Environment()
assets_env.register('css', css)
assets_env.register('js', js)
