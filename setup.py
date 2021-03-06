from distutils.core import setup

setup(
  name = 'beryl',
  packages = ['beryl'],
  package_dir = {'beryl': 'beryl'},
  package_data = {'beryl': ['__init__.py','recorder.py','cache/text.txt']},
  version = '1.9',
  description = 'Makes Writing Tests Super Easy and Quick',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/beryl',
  download_url = 'https://github.com/DanielJDufour/beryl/tarball/download',
  keywords = ['python', 'testing'],
  classifiers = [],
  install_requires=["editdistance","numpy","opencv-python","Pillow","psutil","pytesseract","pyvirtualdisplay","scipy","selenium"]
)
