import unittest
import gpgdir
import os
from unittest import mock
from os import listdir

HOME_DIR = os.path.dirname(os.path.realpath(__file__)) + '/home'


class TestGpgDir(unittest.TestCase):
    @mock.patch('gpgdir.get_home_dir')
    def test_get_home_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(gpgdir.get_home_dir(), HOME_DIR)

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch('gpgdir.get_gpg_dir')
    def test_get_gpg_dir(self, mock_get_gpg_dir, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        mock_get_gpg_dir.return_value = HOME_DIR + '/.gnupg'
        home = gpgdir.get_home_dir()
        self.assertEqual(gpgdir.get_gpg_dir(), home + "/.gnupg")

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch("sys.exit")
    def test_get_gpg_dir_not_exists(self, mock_sys_exit, mock_get_home_dir):
        mock_get_home_dir.return_value = '/abc'
        gpgdir.get_gpg_dir()
        assert mock_sys_exit.called

    @mock.patch('gpgdir.get_home_dir')
    def test_get_key(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(gpgdir.get_key(), "KEYID")

    @mock.patch('gpgdir.os.remove')
    def test_clean_file(self, mocked_remove):
        gpgdir.clean_file('file')
        self.assertTrue(mocked_remove.called)

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch("sys.exit")
    def test_encrypt_dir_not_exists(self, mock_sys_exit, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        gpgdir.encrypt_dir("/abc")
        assert mock_sys_exit.called

    @mock.patch('gpgdir.os.remove')
    @mock.patch('gpgdir.glob.glob')
    def test_encrypt_dir(self, mock_glob, mocked_remove):
        dir_to_encrypt = HOME_DIR + "/test"
        mock_glob.return_value = [os.path.join(dir_to_encrypt, 'test.txt'), os.path.join(dir_to_encrypt, 'test1.txt')]
        gpgdir.encrypt_dir(dir_to_encrypt)
        mock_glob.assert_called_with(os.path.join(dir_to_encrypt, '*'), recursive=True)
        self.assertTrue(len(listdir(dir_to_encrypt)))
        self.assertTrue(mocked_remove.called)

    @mock.patch('getpass.getpass')
    def test_get_password(self, getpw):
        getpw.return_value = 'pass'
        self.assertEqual(gpgdir.get_password(), 'pass')

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch("sys.exit")
    @mock.patch('getpass.getpass')
    def test_decrypt_dir_not_exists(self, getpw, mock_sys_exit, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        getpw.return_value = 'pass'
        gpgdir.decrypt_dir("/abc")
        assert mock_sys_exit.called

    @mock.patch('gpgdir.os.remove')
    @mock.patch('gpgdir.glob.glob')
    @mock.patch('getpass.getpass')
    def test_decrypt_dir(self, getpw, mock_glob, mocked_remove):
        dir_to_decrypt = HOME_DIR + "/test"
        getpw.return_value = 'pass'
        mock_glob.return_value = [os.path.join(dir_to_decrypt, 'test.txt.gpg'),
                                  os.path.join(dir_to_decrypt, 'test1.txt.gpg')]
        gpgdir.decrypt_dir(dir_to_decrypt)
        mock_glob.assert_called_with(os.path.join(dir_to_decrypt, '*.gpg'), recursive=True)
        self.assertTrue(len(listdir(dir_to_decrypt)))
        self.assertTrue(mocked_remove.called)


if __name__ == '__main__':
    unittest.main()
