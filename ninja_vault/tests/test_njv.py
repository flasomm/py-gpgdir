import unittest
import ninja_vault as njv
import os
from unittest import mock

HOME_DIR = os.path.dirname(os.path.realpath(__file__)) + '/home'
DIR_TO_TEST = HOME_DIR + '/test'
GPG_CONF = HOME_DIR + '/.gnupg/gpg.conf'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestIsHidden(unittest.TestCase):
    def test_hidden_file(self):
        self.assertTrue(njv._is_hidden('/home/user/.hidden'))

    def test_hidden_dir(self):
        self.assertTrue(njv._is_hidden('/home/user/.config/file.txt'))

    def test_not_hidden(self):
        self.assertFalse(njv._is_hidden('/home/user/documents/file.txt'))

    def test_not_hidden_relative(self):
        self.assertFalse(njv._is_hidden('some/normal/file.txt'))


class TestIterFiles(unittest.TestCase):
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_yields_regular_files(self, mock_glob, mock_isfile):
        mock_glob.return_value = [DIR_TO_TEST + '/a.txt', DIR_TO_TEST + '/b.txt']
        result = list(njv._iter_files(DIR_TO_TEST))
        self.assertEqual(len(result), 2)

    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_skips_hidden_files(self, mock_glob, mock_isfile):
        mock_glob.return_value = [DIR_TO_TEST + '/.hidden/a.txt', DIR_TO_TEST + '/b.txt']
        result = list(njv._iter_files(DIR_TO_TEST))
        self.assertEqual(len(result), 1)
        self.assertIn(DIR_TO_TEST + '/b.txt', result)

    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_skips_extensions(self, mock_glob, mock_isfile):
        mock_glob.return_value = [DIR_TO_TEST + '/a.gpg', DIR_TO_TEST + '/b.txt']
        result = list(njv._iter_files(DIR_TO_TEST, skip_extensions=('.gpg',)))
        self.assertEqual(result, [DIR_TO_TEST + '/b.txt'])

    @mock.patch('ninja_vault.os.path.isfile', return_value=False)
    @mock.patch('ninja_vault.glob.glob')
    def test_skips_directories(self, mock_glob, mock_isfile):
        mock_glob.return_value = [DIR_TO_TEST + '/subdir']
        result = list(njv._iter_files(DIR_TO_TEST))
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class TestGetHomeDir(unittest.TestCase):
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_home_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(njv.get_home_dir(), HOME_DIR)


class TestGetGnupgDir(unittest.TestCase):
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_gpg_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(njv.get_gpg_dir(), os.path.join(HOME_DIR, '.gnupg'))

    @mock.patch('ninja_vault.get_home_dir')
    def test_get_gpg_dir_not_exists_raises(self, mock_get_home_dir):
        mock_get_home_dir.return_value = '/nonexistent'
        self.assertRaises(Exception, njv.get_gpg_dir)


class TestGetKey(unittest.TestCase):
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_key(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(njv.get_key(), 'KEYID')

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_key_missing_rc_file_exits(self, mock_get_home_dir, mock_exit):
        mock_get_home_dir.return_value = '/nonexistent'
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, njv.get_key)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

class TestCleanFile(unittest.TestCase):
    @mock.patch('ninja_vault.os.remove')
    def test_clean_file_calls_remove(self, mocked_remove):
        njv.clean_file('file.txt')
        mocked_remove.assert_called_once_with('file.txt')

    @mock.patch('ninja_vault.os.remove', side_effect=OSError)
    def test_clean_file_returns_false_on_oserror(self, mocked_remove):
        self.assertFalse(njv.clean_file('file.txt'))


class TestGetPassword(unittest.TestCase):
    @mock.patch('getpass.getpass', return_value='secret')
    def test_get_password_returns_value(self, mock_getpass):
        self.assertEqual(njv.get_password(), 'secret')

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('getpass.getpass', return_value='')
    def test_get_password_empty_exits(self, mock_getpass, mock_exit):
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, njv.get_password)
        mock_exit.assert_called_once_with(1)

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('getpass.getpass', side_effect=Exception('TTY error'))
    def test_get_password_exception_exits(self, mock_getpass, mock_exit):
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, njv.get_password)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# encrypt_dir
# ---------------------------------------------------------------------------

class TestEncryptDir(unittest.TestCase):
    def test_encrypt_dir_not_exists_raises(self):
        self.assertRaises(Exception, njv.encrypt_dir, '/nonexistent')

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_encrypts_all_files(self, mock_glob, mock_isfile,
                                            mock_get_gpg, mock_get_key, mock_clean):
        files = [DIR_TO_TEST + '/sub/test.txt', DIR_TO_TEST + '/test.txt', DIR_TO_TEST + '/test1.txt']
        mock_glob.return_value = files
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.encrypt_file.call_count, 3)
        self.assertEqual(mock_clean.call_count, 3)

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_skips_gpg_files(self, mock_glob, mock_isfile,
                                         mock_get_gpg, mock_get_key, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/already.gpg', DIR_TO_TEST + '/normal.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.encrypt_file.call_count, 1)

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_skips_hidden_files(self, mock_glob, mock_isfile,
                                            mock_get_gpg, mock_get_key, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/.hidden/secret.txt', DIR_TO_TEST + '/normal.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.encrypt_file.call_count, 1)

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.clean_file', return_value=False)
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_delete_failure_exits(self, mock_glob, mock_isfile,
                                              mock_get_gpg, mock_get_key,
                                              mock_clean, mock_exit):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, njv.encrypt_dir, DIR_TO_TEST)
        mock_exit.assert_called_once_with(1)

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_no_delete_does_not_remove_original(self, mock_glob, mock_isfile,
                                                            mock_get_gpg, mock_get_key,
                                                            mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST, delete_original=False)

        mock_clean.assert_not_called()

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_dry_run_skips_gpg_and_delete(self, mock_glob, mock_isfile,
                                                      mock_get_gpg, mock_get_key,
                                                      mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']

        njv.encrypt_dir(DIR_TO_TEST, dry_run=True)

        mock_get_gpg.return_value.encrypt_file.assert_not_called()
        mock_clean.assert_not_called()

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_gpg_failure_exits(self, mock_glob, mock_isfile,
                                           mock_get_gpg, mock_get_key, mock_exit):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=False, stderr='GPG error')
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, njv.encrypt_dir, DIR_TO_TEST)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# decrypt_dir
# ---------------------------------------------------------------------------

class TestDecryptDir(unittest.TestCase):
    def test_decrypt_dir_not_exists_raises(self):
        self.assertRaises(Exception, njv.decrypt_dir, '/nonexistent')

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_decrypts_all_files(self, mock_glob, mock_isfile, mock_reload,
                                            mock_getpw, mock_get_gpg, mock_clean):
        files = [DIR_TO_TEST + '/sub/test.txt.gpg', DIR_TO_TEST + '/test.txt.gpg']
        mock_glob.return_value = files
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status

        njv.decrypt_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.decrypt_file.call_count, 2)
        self.assertEqual(mock_clean.call_count, 2)
        mock_reload.assert_called_once()

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_skips_hidden_files(self, mock_glob, mock_isfile, mock_reload,
                                            mock_getpw, mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/.hidden/secret.txt.gpg', DIR_TO_TEST + '/normal.txt.gpg']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status

        njv.decrypt_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.decrypt_file.call_count, 1)

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.clean_file', return_value=False)
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_delete_failure_exits(self, mock_glob, mock_isfile, mock_reload,
                                              mock_getpw, mock_get_gpg, mock_clean,
                                              mock_exit):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.gpg']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, njv.decrypt_dir, DIR_TO_TEST)
        mock_exit.assert_called_once_with(1)

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_no_delete_does_not_remove_encrypted(self, mock_glob, mock_isfile,
                                                              mock_reload, mock_getpw,
                                                              mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.gpg']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status

        njv.decrypt_dir(DIR_TO_TEST, delete_original=False)

        mock_clean.assert_not_called()

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_dry_run_skips_gpg_and_delete(self, mock_glob, mock_isfile,
                                                      mock_reload, mock_getpw,
                                                      mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.gpg']

        njv.decrypt_dir(DIR_TO_TEST, dry_run=True)

        mock_get_gpg.return_value.decrypt_file.assert_not_called()
        mock_clean.assert_not_called()

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_gpg_failure_exits(self, mock_glob, mock_isfile, mock_reload,
                                           mock_getpw, mock_get_gpg, mock_exit):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.gpg']
        mock_status = mock.MagicMock(ok=False, stderr='GPG error')
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, njv.decrypt_dir, DIR_TO_TEST)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# sign_dir
# ---------------------------------------------------------------------------

class TestSignDir(unittest.TestCase):
    def test_sign_dir_not_exists_raises(self):
        self.assertRaises(Exception, njv.sign_dir, '/nonexistent')

    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_sign_dir_signs_all_files(self, mock_glob, mock_isfile, mock_reload,
                                      mock_getpw, mock_get_gpg, mock_get_key):
        files = [DIR_TO_TEST + '/sub/test.txt', DIR_TO_TEST + '/test.txt']
        mock_glob.return_value = files
        mock_status = mock.MagicMock()
        mock_status.__bool__ = lambda s: True
        mock_get_gpg.return_value.sign_file.return_value = mock_status

        njv.sign_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.sign_file.call_count, 2)
        mock_reload.assert_called_once()

    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_sign_dir_skips_gpg_and_sig_files(self, mock_glob, mock_isfile, mock_reload,
                                               mock_getpw, mock_get_gpg, mock_get_key):
        mock_glob.return_value = [
            DIR_TO_TEST + '/already.gpg',
            DIR_TO_TEST + '/already.sig',
            DIR_TO_TEST + '/normal.txt',
        ]
        mock_status = mock.MagicMock()
        mock_status.__bool__ = lambda s: True
        mock_get_gpg.return_value.sign_file.return_value = mock_status

        njv.sign_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.sign_file.call_count, 1)

    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_sign_dir_skips_hidden_files(self, mock_glob, mock_isfile, mock_reload,
                                         mock_getpw, mock_get_gpg, mock_get_key):
        mock_glob.return_value = [DIR_TO_TEST + '/.hidden/secret.txt', DIR_TO_TEST + '/normal.txt']
        mock_status = mock.MagicMock()
        mock_status.__bool__ = lambda s: True
        mock_get_gpg.return_value.sign_file.return_value = mock_status

        njv.sign_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.sign_file.call_count, 1)

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_sign_dir_failure_exits(self, mock_glob, mock_isfile, mock_reload,
                                    mock_getpw, mock_get_gpg, mock_get_key, mock_exit):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock()
        mock_status.__bool__ = lambda s: False
        mock_get_gpg.return_value.sign_file.return_value = mock_status
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, njv.sign_dir, DIR_TO_TEST)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# verify_dir
# ---------------------------------------------------------------------------

class TestVerifyDir(unittest.TestCase):
    def test_verify_dir_not_exists_raises(self):
        self.assertRaises(Exception, njv.verify_dir, '/nonexistent')

    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.print')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_verify_dir_not_verbose_does_not_print_file_logs(self, mock_glob, mock_isfile,
                                                              mock_print,
                                                              mock_get_gpg):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.sig']
        mock_verified = mock.MagicMock()
        mock_verified.__bool__ = lambda s: True
        mock_get_gpg.return_value.verify_file.return_value = mock_verified

        njv.verify_dir(DIR_TO_TEST, verbose=False)

        mock_print.assert_called_once_with('Verifying dir: ' + DIR_TO_TEST)

    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_verify_dir_verifies_all_files(self, mock_glob, mock_isfile, mock_get_gpg):
        files = [DIR_TO_TEST + '/sub/test.txt.sig', DIR_TO_TEST + '/test.txt.sig']
        mock_glob.return_value = files
        mock_verified = mock.MagicMock()
        mock_verified.__bool__ = lambda s: True
        mock_get_gpg.return_value.verify_file.return_value = mock_verified

        njv.verify_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.verify_file.call_count, 2)

    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_verify_dir_skips_hidden_files(self, mock_glob, mock_isfile, mock_get_gpg):
        mock_glob.return_value = [DIR_TO_TEST + '/.hidden/secret.txt.sig', DIR_TO_TEST + '/normal.txt.sig']
        mock_verified = mock.MagicMock()
        mock_verified.__bool__ = lambda s: True
        mock_get_gpg.return_value.verify_file.return_value = mock_verified

        njv.verify_dir(DIR_TO_TEST)

        self.assertEqual(mock_get_gpg.return_value.verify_file.call_count, 1)

    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_verify_dir_invalid_signature_raises(self, mock_glob, mock_isfile, mock_get_gpg):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.sig']
        mock_verified = mock.MagicMock()
        mock_verified.__bool__ = lambda s: False
        mock_get_gpg.return_value.verify_file.return_value = mock_verified

        self.assertRaises(ValueError, njv.verify_dir, DIR_TO_TEST)


# ---------------------------------------------------------------------------
# get_default_key
# ---------------------------------------------------------------------------

class TestGetDefaultKey(unittest.TestCase):
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_default_key(self, mock_home):
        mock_home.return_value = HOME_DIR
        gpg_conf_content = '# comment\ndefault-key ABCD1234\n'
        with mock.patch('ninja_vault.os.path.isfile', return_value=True), \
             mock.patch('builtins.open', mock.mock_open(read_data=gpg_conf_content)):
            self.assertEqual(njv.get_default_key(), 'ABCD1234')

    @mock.patch('ninja_vault.get_home_dir')
    def test_get_default_key_with_home_dir(self, mock_home):
        mock_home.return_value = HOME_DIR
        gpg_conf_content = 'default-key  MYKEY99\n'
        with mock.patch('ninja_vault.os.path.isfile', return_value=True), \
             mock.patch('builtins.open', mock.mock_open(read_data=gpg_conf_content)):
            self.assertEqual(njv.get_default_key(home_dir=HOME_DIR), 'MYKEY99')

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_default_key_missing_conf_exits(self, mock_home, mock_exit):
        mock_home.return_value = HOME_DIR
        mock_exit.side_effect = SystemExit
        with mock.patch('ninja_vault.os.path.isfile', return_value=False):
            self.assertRaises(SystemExit, njv.get_default_key)
        mock_exit.assert_called_once_with(1)

    @mock.patch('ninja_vault.sys.exit')
    @mock.patch('ninja_vault.get_home_dir')
    def test_get_default_key_not_defined_exits(self, mock_home, mock_exit):
        mock_home.return_value = HOME_DIR
        mock_exit.side_effect = SystemExit
        gpg_conf_content = '# no default-key line here\n'
        with mock.patch('builtins.open', mock.mock_open(read_data=gpg_conf_content)):
            self.assertRaises(SystemExit, njv.get_default_key)
        mock_exit.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Options: key_id, home_dir, verbose propagation
# ---------------------------------------------------------------------------

class TestEncryptDirOptions(unittest.TestCase):
    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_uses_provided_key_id(self, mock_glob, mock_isfile,
                                               mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST, key_id='CUSTOM_KEY')

        call_kwargs = mock_get_gpg.return_value.encrypt_file.call_args
        self.assertIn('CUSTOM_KEY', call_kwargs[1]['recipients'])

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_passes_verbose_to_gpg(self, mock_glob, mock_isfile,
                                                mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST, key_id='K', verbose=True)

        mock_get_gpg.assert_called_once_with(home_dir=None, verbose=True)

    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_passes_home_dir(self, mock_glob, mock_isfile,
                                         mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST, key_id='K', home_dir='/custom/home')

        mock_get_gpg.assert_called_once_with(home_dir='/custom/home', verbose=False)


class TestDecryptDirOptions(unittest.TestCase):
    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_decrypt_dir_passes_home_dir_and_verbose(self, mock_glob, mock_isfile,
                                                      mock_reload, mock_getpw,
                                                      mock_get_gpg, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt.gpg']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.decrypt_file.return_value = mock_status

        njv.decrypt_dir(DIR_TO_TEST, home_dir='/custom/home', verbose=True)

        mock_get_gpg.assert_called_once_with(home_dir='/custom/home', verbose=True)


class TestDeleteAndDryRunOptions(unittest.TestCase):
    @mock.patch('ninja_vault.clean_file')
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_encrypt_dir_delete_true_calls_clean(self, mock_glob, mock_isfile,
                                                mock_get_gpg, mock_get_key, mock_clean):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock(ok=True)
        mock_get_gpg.return_value.encrypt_file.return_value = mock_status

        njv.encrypt_dir(DIR_TO_TEST, delete_original=True)

        mock_clean.assert_called_once()


class TestSignDirOptions(unittest.TestCase):
    @mock.patch('ninja_vault.get_key', return_value='TESTKEY')
    @mock.patch('ninja_vault._get_gpg')
    @mock.patch('ninja_vault.get_password', return_value='secret')
    @mock.patch('ninja_vault._reload_agent')
    @mock.patch('builtins.open', mock.mock_open(read_data=b'data'))
    @mock.patch('ninja_vault.os.path.isfile', return_value=True)
    @mock.patch('ninja_vault.glob.glob')
    def test_sign_dir_uses_provided_key_id(self, mock_glob, mock_isfile, mock_reload,
                                            mock_getpw, mock_get_gpg, mock_get_key):
        mock_glob.return_value = [DIR_TO_TEST + '/test.txt']
        mock_status = mock.MagicMock()
        mock_status.__bool__ = lambda s: True
        mock_get_gpg.return_value.sign_file.return_value = mock_status

        njv.sign_dir(DIR_TO_TEST, key_id='OVERRIDE_KEY')

        call_kwargs = mock_get_gpg.return_value.sign_file.call_args
        self.assertEqual(call_kwargs[1]['keyid'], 'OVERRIDE_KEY')
        mock_get_key.assert_not_called()


if __name__ == '__main__':
    unittest.main()
