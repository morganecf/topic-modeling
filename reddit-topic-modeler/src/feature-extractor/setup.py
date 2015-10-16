from distutils.core import setup


setup(
    name = 'Twitter Feature Extractor',
    version = '0.0.3',
    scripts = ['bin/tfx'],
    packages = ['tfx'],
    package_dir = {'tfx': 'src/tfx'},
    package_data = {'tfx': ['resources/*']},
)
