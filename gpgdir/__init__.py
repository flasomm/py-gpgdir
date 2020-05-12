import sys
import gnupg
import os


def get_home_dir():
    return os.path.expanduser('~')


def get_gpg_dir():
    gpg_homedir = get_home_dir() + "/.gnupg"
    if not os.path.isdir(gpg_homedir):
        print(
            "[*] GnuPG directory: "
            + gpg_homedir +
            " does not exist.\n Please create it by executing: \"gpg --gen-key\". Exiting.\n"
        )
        sys.exit()

    return gpg_homedir


def get_key():
    gpgdirrc_file = get_home_dir() + "/.gpgdirrc"
    if not os.path.isfile(gpgdirrc_file):
        print("[*] Please edit " + gpgdirrc_file + " to include your gpg key identifier\n",
              "    (e.g. \"D4696445\"; see the output of \"gpg --list-keys\"), or use the\n",
              "    default GnuPG key defined in ~/.gnupg/options")

    with open(gpgdirrc_file, "r") as fi:
        key = ''
        for ln in fi:
            if ln.startswith("use_key"):
                key = ln[2:]
    print(key)


def usage():
    print("""
py-gpgdir; Recursive direction encryption and decryption with GnuPG

[+] Version: $version
    Author:  Fabrice Sommavilla
    URL:     https://github.com/flasomm/py-gpgdir.git

Usage: py-gpgdir -e|-d <directory> [options]

Options:
    -e, --encrypt <directory>   - Recursively encrypt all files in
                                  <directory> and all subdirectories.
    -d, --decrypt <directory>   - Recursively decrypt all files in
                                  <directory> and all subdirectories.
    --sign <directory>          - Recursively sign all files in <directory>
                                  and all subdirectories.
    --verify <directory>        - Recursively verify all GnuPG signatures
                                  in <directory>.
    -K, --Key-id <id>           - Specify GnuPG key ID, or key-matching
                                  string. This overrides the use_key value
                                  in ~/.gpgdirrc
    -D, --Default-key           - Use the key that GnuPG defines as the
                                  default (i.e. the key that is specified
                                  by the default-key option in
                                  ~/.gnupg/options).
    -g, --gnupg-dir <dir>       - Specify a path to a .gnupg directory for
                                  gpg keys (the default is ~/.gnupg if this
                                  option is not used).
    --verbose                   - Run in verbose mode.
    -V, --Version               - print version.
    -h, --help                  - print help.

    """)
    sys.exit()
