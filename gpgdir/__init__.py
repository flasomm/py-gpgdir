import sys
import os
import configparser
import glob
import gnupg


def get_home_dir():
    return os.path.expanduser('~')


def get_gpg_dir():
    gpg_homedir = get_home_dir() + "/.gnupg"
    if not os.path.isdir(gpg_homedir):
        print(
            "[*] GnuPG directory: "
            + gpg_homedir + " does not exist.\n"
            + "Please create it by executing: \"gpg --gen-key\"."
        )
        sys.exit(1)
    return gpg_homedir


def get_key():
    gpgdirrc_file = get_home_dir() + "/.py_gpgdirrc"
    if not os.path.isfile(gpgdirrc_file):
        print("[*] Please edit " + gpgdirrc_file + " to include your gpg key identifier")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(gpgdirrc_file)
    return config['DEFAULT']['UseKey']


def encrypt_dir(dir_to_encrypt):
    if not os.path.isdir(dir_to_encrypt):
        print("[*] Directory to encrypt: " + dir_to_encrypt + " does not exist.\n")
        sys.exit(1)

    gpg = gnupg.GPG(gnupghome=get_home_dir() + "/.gnupg", verbose=True)
    print("Encrypt dir: " + dir_to_encrypt)
    for file in list(glob.glob(dir_to_encrypt + "/*")):
        with open(file, 'rb') as f:
            status = gpg.encrypt_file(
                file=f,
                recipients=['flasomm@gmail.com'],
                output=file + '.gpg',
            )
        print(status.ok)
        print(status.status)
        print(status.stderr)
        print('~' * 50)

    # gpg --output myfile.txt.gpg --encrypt --recipient your.friend@yourfriendsdomain.com  myfile.txt
