import unittest
from unittest import mock
import gpgdir
import os

HOME_DIR = os.path.dirname(os.path.realpath(__file__)) + '/home'


class TestGpgDir(unittest.TestCase):
    @mock.patch('gpgdir.get_home_dir')
    def test_get_home_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(gpgdir.get_home_dir(), HOME_DIR)

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch('gpgdir.get_gpg_dir')
    def test_get_gpg_dir_exists(self, mock_get_gpg_dir, mock_get_home_dir):
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

    @mock.patch('gpgdir.get_home_dir')
    def test_encrypt_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(gpgdir.get_key(), "KEYID")


if __name__ == '__main__':
    unittest.main()
