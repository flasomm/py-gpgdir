import sys
import os
import configparser
import glob
import gnupg
import getpass


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


def clean_files(dir_to_scan, is_gpg=True):
    pattern = "/*.gpg" if is_gpg else "/[!.gpg]*"
    files_to_remove = list(glob.glob(dir_to_scan + pattern, recursive=True))
    if m.lower().endswith(('.png', '.jpg', '.jpeg'))
    [os.remove(f) for f in files_to_remove]


def encrypt_dir(dir_to_encrypt):
    if not os.path.isdir(dir_to_encrypt):
        print("[*] Directory to encrypt: " + dir_to_encrypt + " does not exist.\n")
        sys.exit(1)

    print("Encrypt dir: " + dir_to_encrypt)
    gpg = gnupg.GPG(gnupghome=get_home_dir() + "/.gnupg", verbose=True)
    for file in list(glob.glob(dir_to_encrypt + "/*", recursive=True)):
        with open(file, 'rb') as f:
            status = gpg.encrypt_file(
                file=f,
                recipients=[get_key()],
                output=file + '.gpg',
            )
        print(status.ok)
        print(status.status)
        print(status.stderr)
        print('~' * 50)

    #clean_files(dir_to_encrypt, False)


def get_password():
    try:
        password = getpass.getpass()
    except Exception as error:
        print('Error getting password', error)
    else:
        return password


def decrypt_dir(dir_to_decrypt):
    if not os.path.isdir(dir_to_decrypt):
        print("[*] Directory to decrypt: " + dir_to_decrypt + " does not exist.\n")
        sys.exit(1)

    password = get_password()
    gpg = gnupg.GPG(gnupghome=get_home_dir() + "/.gnupg", verbose=True)
    print("Decrypt dir: " + dir_to_decrypt)
    for file in list(glob.glob(dir_to_decrypt + "/*.gpg", recursive=True)):
        with open(file, 'rb') as f:
            status = gpg.decrypt_file(
                file=f,
                passphrase=password,
                output=file,
            )
        print(status.ok)
        print(status.status)
        print(status.stderr)

    clean_files(dir_to_decrypt)
