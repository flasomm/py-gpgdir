from setuptools import setup

setup(name='py-gpgdir',
      version='0.1',
      description='py-gpgdir is a python script that uses recursively encrypt and decrypt directories using gpg',
      url='https://github.com/flasomm/py-gpgdir.git',
      author='Fabrice Sommavilla',
      author_email='fs@physalix.com',
      license='MIT',
      packages=['gpgdir'],
      scripts=['bin/pygpgdir'],
      zip_safe=False)
