from setuptools import setup

setup(name='py-gpgdir',
      version='0.1',
      description='py-gpgdir is a python script that uses recursively encrypt and decrypt directories using gpg',
      classifiers=[
          'Development Status :: 0.1',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.8'
      ],
      keywords='gpgdir, gpg, encrypt, decrypt, directory',
      url='https://github.com/flasomm/py-gpgdir.git',
      author='Fabrice Sommavilla',
      author_email='fs@physalix.com',
      license='MIT',
      packages=['gpgdir'],
      install_requires=[
          'gnupg'
      ],
      scripts=['bin/pygpgdir'],
      zip_safe=False)
