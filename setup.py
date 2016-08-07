from distutils.core import setup

setup(
  name = 'breeze',
  packages = ['breeze'],
  package_dir = {'breeze': 'breeze'},
  package_data = {'breeze': ['__init__.py']},
  version = '0.1',
  description = 'Makes Writing Tests A Breeze',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/breeze',
  download_url = 'https://github.com/DanielJDufour/breeze/tarball/download',
  keywords = ['python', 'testing'],
  classifiers = [],
)
