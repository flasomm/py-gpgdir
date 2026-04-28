# Pygpgdir - Recursive directory encryption with GnuPG

pygpgdir is a python script that uses the python-gnupg module to encrypt and decrypt directories using a gpg key 
specified in ~/.py_gpgdirrc.

pygpgdir recursively descends through a directory in order to encrypt, decrypt, sign, or verify every file in 
a directory and all of its subdirectories. In addition, gpgdir is careful to not encrypt hidden files and directories.
It should be noted that pygpgdir is not intended as a replacement or competitor to good filesystem encryption solutions 
such as encfs - it is merely an effort to apply GnuPG recursively to files since GnuPG itself doesn't offer this capability.

By default, pygpgdir deletes original files after successful encryption and decryption.
Use --no-delete to keep originals.
Use --dry-run to preview actions without writing or deleting files.

After all, you probably don't want your ~/.py_gpgdirrc directory or ~/.bashrc file to be encrypted. 
The GnuPG key gpgdir uses to encrypt/decrypt a directory is specified in ~/.py_gpgdirrc. 

pygpgdir currently removes files using standard filesystem deletion.

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
a detached .sig signature will be created.

`--verify` - Recursively verify every .sig file in the directory specified on the command line.

`-K`, `--Key-id <id>` - Manually specify a GnuPG key ID from the command line. Because GnuPG supports matching keys 
with a string, id does not strictly have to be a key ID; it can be a string that uniquely matches a key in the GnuPG 
key ring.

`-D`, `--Default-key` - Use the key defined by `default-key` in `~/.gnupg/gpg.conf`.

`-g`, `--gnupg-dir <dir>` - Use an alternate home directory containing `.gnupg` and `.py_gpgdirrc`.

`-u`, `--user-homedir <dir>` - Alias of `--gnupg-dir`.

`--no-delete` - Keep source files after successful encrypt/decrypt.

`--dry-run` - Show planned encrypt/decrypt operations without modifying files.

`--verbose` - Will print verbose info during the execution.

`-V`, `--Version` - Display the version of this tool.

`-h`, `--help` - Will print a list of available commands and options.

### Test
```bash
python -m pytest gpgdir/tests/test_gpgdir.py -v
```

