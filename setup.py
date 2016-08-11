from distutils.core import setup

setup(
  name = 'dust',
  packages = ['dust'],
  package_dir = {'dust': 'dust'},
  package_data = {'dust': ['__init__.py','recorder.py']},
  version = '0.3',
  description = 'Makes Writing Tests A Breeze',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/dust',
  download_url = 'https://github.com/DanielJDufour/dust/tarball/download',
  keywords = ['python', 'testing'],
  classifiers = [],
)
