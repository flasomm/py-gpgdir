from pkg_resources import get_distribution
import sys
import os
import configparser
import glob
import gnupg
import getpass


def get_version():
    print(get_distribution('py-gpgdir'))


def get_home_dir():
    return os.path.expanduser('~')


def check_directory_exists(dir, message):
    if not os.path.isdir(dir):
        raise Exception('[*] ' + message + ': ' + dir + ' does not exist.\n')


def get_gpg_dir():
    gpg_homedir = os.path.join(get_home_dir(), '.gnupg')
    check_directory_exists(gpg_homedir, 'GnuPG directory')
    return gpg_homedir


def get_key():
    gpgdirrc_file = os.path.join(get_home_dir(), '.py_gpgdirrc')
    if not os.path.isfile(gpgdirrc_file):
        print('[*] Please edit ' + gpgdirrc_file + ' to include your gpg key identifier')
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(gpgdirrc_file)
    return config['DEFAULT']['UseKey']


def clean_file(file):
    try:
        os.remove(file)
    except OSError:
        pass


def get_password():
    try:
        password = getpass.getpass()
    except Exception as error:
        print('Error getting password', error)
    else:
        return password


def encrypt_dir(dir_to_encrypt):
    check_directory_exists(dir_to_encrypt, 'Directory to encrypt')
    print('Encrypting dir: ' + dir_to_encrypt)
    gpg = gnupg.GPG(gnupghome=os.path.join(get_home_dir(), '.gnupg'), verbose=False)

    for file in glob.glob(os.path.join(dir_to_encrypt, '**/*'), recursive=True):
        if os.path.isfile(file):
            print('[+] encrypting: ' + file)
            with open(file, 'rb') as f:
                status = gpg.encrypt_file(
                    file=f,
                    recipients=[get_key()],
                    output=file + '.gpg'
                )
            if status.ok:
                clean_file(file)
            else:
                print(status.stderr)
                sys.exit(1)


def decrypt_dir(dir_to_decrypt):
    check_directory_exists(dir_to_decrypt, 'Directory to decrypt')
    print('Decrypting dir: ' + dir_to_decrypt)
    os.system('gpgconf --reload gpg-agent')
    password = get_password()
    gpg = gnupg.GPG(gnupghome=os.path.join(get_home_dir(), '.gnupg'), verbose=False)

    for file in glob.glob(os.path.join(dir_to_decrypt, '**/*.gpg'), recursive=True):
        print('[+] decrypting: ' + file)
        with open(file, 'rb') as f:
            status = gpg.decrypt_file(
                file=f,
                passphrase=password,
                output=os.path.splitext(file)[0],
            )
        if status.ok:
            clean_file(file)
        else:
            print(status.stderr)
            sys.exit(1)


def sign_dir(dir_to_sign):
    check_directory_exists(dir_to_sign, 'Directory to sign')
    print('Signing dir: ' + dir_to_sign)
    os.system('gpgconf --reload gpg-agent')
    password = get_password()
    gpg = gnupg.GPG(gnupghome=os.path.join(get_home_dir(), '.gnupg'), verbose=False)

    for file in glob.glob(os.path.join(dir_to_sign, '**/*'), recursive=True):
        if os.path.isfile(file) and not (file.endswith('.gpg') or file.endswith('.sig')):
            print('[+] signing: ' + file)
            with open(file, 'rb') as f:
                gpg.sign_file(
                    f,
                    keyid=get_key(),
                    passphrase=password,
                    output=file + '.sig'
                )


def verify_dir(dir_to_verify):
    check_directory_exists(dir_to_verify, 'Directory to verify')
    print('Verifying dir: ' + dir_to_verify)
    gpg = gnupg.GPG(gnupghome=os.path.join(get_home_dir(), '.gnupg'), verbose=False)

    for file in glob.glob(os.path.join(dir_to_verify, '**/*'), recursive=True):
        if os.path.isfile(file) and file.endswith('.sig'):
            print('[+] verifying: ' + file)
            with open(file, 'rb') as f:
                verified = gpg.verify_file(f)
                if not verified:
                    raise ValueError("Signature could not be verified!")
                else:
                    print('verified')
