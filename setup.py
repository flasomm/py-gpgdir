from setuptools import setup

setup(name='ninja-vault',
    version='0.2.0',
      description='ninja-vault is a Python CLI for recursive directory encryption, decryption, signing and verification using GnuPG',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.8'
      ],
      keywords='gpg, encrypt, decrypt, directory, ninja-vault',
      url='https://github.com/flasomm/ninja-vault.git',
      author='Fabrice Sommavilla',
      author_email='fs@physalix.com',
      license='MIT',
      packages=['ninja_vault'],
      install_requires=[
          'python-gnupg',
          'tqdm',
          'wheel',
          'setuptools'
      ],
      scripts=['bin/py-njv'],
      zip_safe=False)
