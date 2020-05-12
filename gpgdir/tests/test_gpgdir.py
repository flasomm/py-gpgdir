import unittest
from unittest import mock
import gpgdir


class TestGpgDir(unittest.TestCase):
    @mock.patch('gpgdir.get_home_dir')
    def test_get_home_dir(self, mock_get_home_dir):
        mock_get_home_dir.return_value = '/abc'
        self.assertEqual(gpgdir.get_home_dir(), "/abc")

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch('gpgdir.get_gpg_dir')
    def test_get_gpg_dir_exists(self, mock_get_gpg_dir, mock_get_home_dir):
        mock_get_home_dir.return_value = '/abc'
        mock_get_gpg_dir.return_value = '/abc/.gnupg'
        home = gpgdir.get_home_dir()
        self.assertEqual(gpgdir.get_gpg_dir(), home + "/.gnupg")

    @mock.patch('gpgdir.get_home_dir')
    @mock.patch('gpgdir.get_gpg_dir')
    def test_get_gpg_dir_not_exists(self, mock_get_gpg_dir, mock_get_home_dir):
        mock_get_home_dir.return_value = '/abc'
        mock_get_gpg_dir.return_value = '/abc/.gnupg'
        home = gpgdir.get_home_dir()
        self.assertEqual(gpgdir.get_gpg_dir(), home + "/.gnupg")


if __name__ == '__main__':
    unittest.main()
