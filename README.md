# py-gpgdir

## Install project
pip install .

## Start Unit Tests
python setup.py test

## Encrypt folder
pygpgdir -e gpgdir/tests/home/test/

## Decrypt folder
pygpgdir -d gpgdir/tests/home/test/

## Sign folder
pygpgdir --sign gpgdir/tests/home/test/

## Verify folder
pygpgdir --verify gpgdir/tests/home/test/