# Pygpgdir - Recursive directory encryption with GnuPG

pygpgdir is a python script that uses the python-gnupg module to encrypt and decrypt directories using a gpg key 
specified in ~/.py_gpgdirrc.

pygpgdir recursively descends through a directory in order to encrypt, decrypt, sign, or verify every file in 
a directory and all of its subdirectories. In addition, gpgdir is careful to not encrypt hidden files and directories.
It should be noted that pygpgdir is not intended as a replacement or competitor to good filesystem encryption solutions 
such as encfs - it is merely an effort to apply GnuPG recursively to files since GnuPG itself doesn't offer this capability.

By default, the mtime and atime values of all files will be preserved upon encryption and decryption 
(this can be disabled with the --no-preserve-times option). Note that in --encrypt mode, pygpgdir will delete 
the original files that it successfully encrypts (unless the --no-delete option is given). 

However, upon startup pygpgdir first asks for a the decryption password to be sure that a dummy file can successfully 
be encrypted and decrypted. The initial test can be disabled with the --skip-test option so that a directory can 
easily be encrypted without having to also specify a password (this is consistent with gpg behavior). 

After all, you probably don't want your ~/.py_gpgdirrc directory or ~/.bashrc file to be encrypted. 
The GnuPG key gpgdir uses to encrypt/decrypt a directory is specified in ~/.py_gpgdirrc. 

Also, pygpgdir can use the wipe program with the --Wipe command line option to securely delete the original unencrypted 
files after they have been successfully encrypted. This elevates the security stance of pygpgdir since it is more 
difficult to recover the unencrypted data associated with files from the filesystem after they are encrypted (unlink() does
not erase data blocks even though a file is removed).

### Install

```bash
pip install .
```

### Usage

#### Encrypt folder

```bash
pygpgdir -e <dir>
```

#### Decrypt folder

```bash
pygpgdir -d <dir>
```

#### Sign folder

```bash
pygpgdir --sign <dir>
```

#### Verify folder

```bash
pygpgdir --verify <dir>
```

##### Options

`-e`, `--encrypt` - Recursively encrypt all files in the directory specified on the command line. 
All original files will be deleted (a password check is performed first to make sure that the correct password to 
unlock the private GnuPG key is known to the user).


`-d`, `--decrypt` - Recursively decrypt all files in the directory specified on the command line. 
The encrypted .gpg version of each file will be deleted.

`--sign` - Recursively sign all files in the directory specified on the command line. For each file, 
a detached .asc signature will be created.

`--verify` - Run an encryption and decryption test against a dummy file and exit. This test is always run by default 
in both --encrypt and --decrypt mode.

`-K`, `--Key-id <id>` - Manually specify a GnuPG key ID from the command line. Because GnuPG supports matching keys 
with a string, id does not strictly have to be a key ID; it can be a string that uniquely matches a key in the GnuPG 
key ring.

`-D`, `--Default-key` - Use the key that GnuPG defines as the default, i.e. the key that is specified by the 
default-key variable in ~/.gnupg/options. If the default-key variable is not defined within ~/.gnupg/options, 
then GnuPG tries to use the first suitable key on its key ring (the initial encrypt/decrypt test makes sure that the 
user knows the corresponding password for the key).

`-u`, `--user-homedir`

`--verbose` - Will print verbose info during the execution.

`-V`, `--Version` - Display the version of this tool.

`-h`, `--help` - Will print a list of available commands and options.

`--no-delete`
`--no-preserve-times`
`--skip-test`

### Test
```bash
python setup.py test
```

