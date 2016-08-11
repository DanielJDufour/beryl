from distutils.core import setup

setup(
  name = 'btest',
  packages = ['btest'],
  package_dir = {'btest': 'btest'},
  package_data = {'btest': ['__init__.py','recorder.py']},
  version = '0.5',
  description = 'Makes Writing Tests Super Easy and Quick',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/btest',
  download_url = 'https://github.com/DanielJDufour/btest/tarball/download',
  keywords = ['python', 'testing'],
  classifiers = [],
)
