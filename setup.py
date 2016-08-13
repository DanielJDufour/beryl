from distutils.core import setup

setup(
  name = 'beryl',
  packages = ['beryl'],
  package_dir = {'beryl': 'beryl'},
  package_data = {'beryl': ['__init__.py','recorder.py']},
  version = '0.7',
  description = 'Makes Writing Tests Super Easy and Quick',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/beryl',
  download_url = 'https://github.com/DanielJDufour/beryl/tarball/download',
  keywords = ['python', 'testing'],
  classifiers = [],
)
