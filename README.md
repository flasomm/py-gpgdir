# pygpgdir - Recursive directory encryption with GnuPG

gpgdir is a python script that uses the python-gnupg module to encrypt and decrypt directories using a gpg key 
specified in ~/.py_gpgdirrc.

# Description

gpgdir supports recursively descending through a directory in order to make sure it encrypts or decrypts every file 
in a directory and all of its subdirectories. In addition, gpgdir is careful to not encrypt hidden files and directories. 
Other features include the ability to interface with the wipe program for secure file deletion, 
and the ability to obfuscate the original filenames within encrypted directories. 
It should be noted that gpgdir is not intended as a replacement or competitor to good filesystem encryption solutions 
such as encfs - it is merely an effort to apply GnuPG recursively to files since GnuPG itself doesn't offer this capability.


gpgdir is a perl script that uses the CPAN GnuPG::Interface perl module
to recursively encrypt  and  decrypt  directories  using  gpg.   gpgdir
recursively  descends through a directory in order to encrypt, decrypt,
sign, or verify every file in a directory and all  of  its  subdirecto-
ries.  By default, the mtime and atime values of all files will be pre-
served upon encryption and decryption (this can be  disabled  with  the
--no-preserve-times  option).  Note that in --encrypt mode, gpgdir will
delete the original files that it  successfully  encrypts  (unless  the
--no-delete  option is given).  However, upon startup gpgdir first asks
for a the decryption password to be sure that a dummy file can success-
fully  be  encrypted  and  decrypted.  The initial test can be disabled
with the --skip-test option so that a directory can easily be encrypted
without  having to also specify a password (this is consistent with gpg
behavior).  Also, note that gpgdir is careful not encrypt hidden  files
and  directories.   After  all,  you  probably don't want your ~/.gnupg
directory or ~/.bashrc file to be encrypted.  The GnuPG key gpgdir uses
to  encrypt/decrypt  a  directory  is  specified in ~/.gpgdirrc.  Also,
gpgdir can use the wipe program with the --Wipe command line option  to
securely  delete  the  original  unencrypted files after they have been
successfully encrypted.  This elevates the security  stance  of  gpgdir
since  it  is more difficult to recover the unencrypted data associated
with files from the filesystem after they are encrypted (unlink()  does
not erase data blocks even though a file is removed).

Note  that  gpgdir is not designed to be a replacement for an encrypted
filesystem solution like encfs or ecryptfs.  Rather, it is an  alterna-
tive  that allows one to take advantage of the cryptographic properties
offered by GnuPG in a recursive manner across an existing filesystem.

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
