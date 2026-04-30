from importlib.metadata import version
import sys
import os
import re
import configparser
import glob
import subprocess
import shutil
import gnupg
import getpass

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


_gpg_runtime_checked = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_gpg(home_dir=None, verbose=False):
    """Return a configured GPG instance."""
    _check_gpg_runtime()
    return gnupg.GPG(gnupghome=get_gpg_dir(home_dir=home_dir), verbose=verbose)


def _detect_gpg_major_version():
    """Return the major gpg version number, or None if unknown."""
    try:
        proc = subprocess.run(
            ['gpg', '--version'],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

    if not proc.stdout:
        return None

    first_line = proc.stdout.splitlines()[0]
    match = re.search(r'(\d+)\.', first_line)
    if not match:
        return None
    return int(match.group(1))


def _check_gpg_runtime():
    """Emit a compatibility warning once when runtime looks unsupported."""
    global _gpg_runtime_checked
    if _gpg_runtime_checked:
        return

    major = _detect_gpg_major_version()
    if major is None:
        print('[*] Warning: unable to detect GnuPG version. GnuPG 2.x is recommended.')
    elif major < 2:
        print('[*] Warning: GnuPG 1.x detected. ninja-vault is best supported with GnuPG 2.x.')

    _gpg_runtime_checked = True


def _reload_agent():
    """Reload the gpg-agent so cached credentials are refreshed."""
    if shutil.which('gpgconf') is None:
        return

    try:
        subprocess.run(['gpgconf', '--reload', 'gpg-agent'], check=True)
    except subprocess.SubprocessError:
        # Non-fatal: decrypt/sign can still proceed depending on local GPG setup.
        pass


def _is_hidden(path):
    """Return True if any component of *path* is a hidden file/directory."""
    return any(part.startswith('.') for part in path.split(os.sep) if part)


def _iter_files(directory, pattern='**/*', skip_extensions=()):
    """Yield every non-hidden regular file under *directory*.

    Args:
        directory:        Root path to walk.
        pattern:          Glob pattern relative to *directory*.
        skip_extensions:  Tuple of file extensions to exclude (e.g. '.gpg').
    """
    for file in glob.glob(os.path.join(directory, pattern), recursive=True):
        if not os.path.isfile(file):
            continue
        if _is_hidden(file):
            continue
        if skip_extensions and any(file.endswith(ext) for ext in skip_extensions):
            continue
        yield file


def _with_progress(items, description, enabled=True):
    """Wrap an iterable with a progress bar when available."""
    if not enabled or tqdm is None:
        return items
    return tqdm(items, desc=description, unit='file', dynamic_ncols=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_version():
    print(version('ninja-vault'))


def get_home_dir(home_dir=None):
    return home_dir if home_dir else os.path.expanduser('~')


def check_directory_exists(directory, message):
    if not os.path.isdir(directory):
        raise Exception('[*] ' + message + ': ' + directory + ' does not exist.\n')


def get_gpg_dir(home_dir=None):
    gpg_homedir = os.path.join(get_home_dir(home_dir=home_dir), '.gnupg')
    check_directory_exists(gpg_homedir, 'GnuPG directory')
    return gpg_homedir


def get_key(home_dir=None):
    njvrc_file = os.path.join(get_home_dir(home_dir=home_dir), '.py_njvrc')
    if not os.path.isfile(njvrc_file):
        print('[*] Please edit ' + njvrc_file + ' to include your gpg key identifier')
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(njvrc_file)
    return config['DEFAULT']['UseKey']


def get_default_key(home_dir=None):
    """Read the default-key from ~/.gnupg/gpg.conf."""
    gpg_conf = os.path.join(get_gpg_dir(home_dir=home_dir), 'gpg.conf')
    if not os.path.isfile(gpg_conf):
        print('[*] gpg.conf not found at ' + gpg_conf + ', cannot determine default key.')
        sys.exit(1)
    with open(gpg_conf, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            match = re.match(r'^default-key\s+(\S+)', line)
            if match:
                return match.group(1)
    print('[*] No default-key defined in ' + gpg_conf)
    sys.exit(1)


def clean_file(file):
    try:
        os.remove(file)
        return True
    except OSError as error:
        print('[!] Failed to remove file ' + file + ': ' + str(error))
        return False


def get_password():
    try:
        password = getpass.getpass()
    except Exception as error:
        print('Error getting password', error)
        sys.exit(1)
    if not password:
        print('[*] Password cannot be empty.')
        sys.exit(1)
    return password


def encrypt_dir(
    dir_to_encrypt,
    key_id=None,
    home_dir=None,
    verbose=False,
    delete_original=True,
    dry_run=False,
    progress=True,
):
    check_directory_exists(dir_to_encrypt, 'Directory to encrypt')
    print('Encrypting dir: ' + dir_to_encrypt)
    gpg = _get_gpg(home_dir=home_dir, verbose=verbose)
    key = key_id or get_key(home_dir=home_dir)

    files = list(_iter_files(dir_to_encrypt, skip_extensions=('.gpg',)))
    show_progress = progress and not verbose and not dry_run

    for file in _with_progress(files, 'Encrypting', enabled=show_progress):
        if dry_run:
            print('[DRY-RUN] would encrypt: ' + file + ' -> ' + file + '.gpg')
            continue
        if verbose:
            print('[+] encrypting: ' + file)
        with open(file, 'rb') as f:
            status = gpg.encrypt_file(f, recipients=[key], output=file + '.gpg')
        if status.ok:
            if delete_original and not clean_file(file):
                sys.exit(1)
        else:
            print(status.stderr)
            sys.exit(1)


def decrypt_dir(
    dir_to_decrypt,
    home_dir=None,
    verbose=False,
    delete_original=True,
    dry_run=False,
    progress=True,
):
    check_directory_exists(dir_to_decrypt, 'Directory to decrypt')
    print('Decrypting dir: ' + dir_to_decrypt)
    _reload_agent()
    password = get_password()
    gpg = _get_gpg(home_dir=home_dir, verbose=verbose)

    files = list(_iter_files(dir_to_decrypt, pattern='**/*.gpg'))
    show_progress = progress and not verbose and not dry_run

    for file in _with_progress(files, 'Decrypting', enabled=show_progress):
        if dry_run:
            print('[DRY-RUN] would decrypt: ' + file + ' -> ' + os.path.splitext(file)[0])
            continue
        if verbose:
            print('[+] decrypting: ' + file)
        with open(file, 'rb') as f:
            status = gpg.decrypt_file(
                f,
                passphrase=password,
                output=os.path.splitext(file)[0],
            )
        if status.ok:
            if delete_original and not clean_file(file):
                sys.exit(1)
        else:
            print(status.stderr)
            sys.exit(1)


def sign_dir(dir_to_sign, key_id=None, home_dir=None, verbose=False):
    check_directory_exists(dir_to_sign, 'Directory to sign')
    print('Signing dir: ' + dir_to_sign)
    _reload_agent()
    password = get_password()
    gpg = _get_gpg(home_dir=home_dir, verbose=verbose)
    key = key_id or get_key(home_dir=home_dir)

    files = list(_iter_files(dir_to_sign, skip_extensions=('.gpg', '.sig')))
    show_progress = not verbose

    for file in _with_progress(files, 'Signing', enabled=show_progress):
        if verbose:
            print('[+] signing: ' + file)
        with open(file, 'rb') as f:
            status = gpg.sign_file(f, keyid=key, passphrase=password, output=file + '.sig')
        if not status:
            print('[!] Failed to sign: ' + file)
            sys.exit(1)


def verify_dir(dir_to_verify, home_dir=None, verbose=False):
    check_directory_exists(dir_to_verify, 'Directory to verify')
    print('Verifying dir: ' + dir_to_verify)
    gpg = _get_gpg(home_dir=home_dir, verbose=verbose)

    files = list(_iter_files(dir_to_verify, pattern='**/*.sig'))
    show_progress = not verbose

    for file in _with_progress(files, 'Verifying', enabled=show_progress):
        if verbose:
            print('[+] verifying: ' + file)
        with open(file, 'rb') as f:
            verified = gpg.verify_file(f)
        if not verified:
            raise ValueError('Signature could not be verified: ' + file)
        if verbose:
            print('[+] verified: ' + file)
