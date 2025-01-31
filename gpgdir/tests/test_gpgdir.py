import unittest
import gpgdir
import os
from unittest import mock
from os import listdir

HOME_DIR = os.path.dirname(os.path.realpath(__file__)) + '/home'
dir_to_test = HOME_DIR + "/test"


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
    def test_get_gpg_dir_not_exists(self, mock_get_home_dir):
        mock_get_home_dir.return_value = '/abc'
        self.assertRaises(Exception, gpgdir.sign_dir, '/abc')

    @mock.patch('gpgdir.get_home_dir')
    def test_get_key(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertEqual(gpgdir.get_key(), "KEYID")

    @mock.patch('gpgdir.os.remove')
    def test_clean_file(self, mocked_remove):
        gpgdir.clean_file('file')
        self.assertTrue(mocked_remove.called)

    @mock.patch('gpgdir.get_home_dir')
    def test_encrypt_dir_not_exists(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertRaises(Exception, gpgdir.encrypt_dir, '/abc')

    @mock.patch('gpgdir.os.remove')
    @mock.patch('gpgdir.glob.glob')
    def test_encrypt_dir(self, mock_glob, mocked_remove):
        mock_glob.return_value = [
            os.path.join(dir_to_test, 'sub', 'test.txt'),
            os.path.join(dir_to_test, 'test.txt'),
            os.path.join(dir_to_test, 'test1.txt')
        ]
        gpgdir.encrypt_dir(dir_to_test)
        mock_glob.assert_called_with(os.path.join(dir_to_test, '**/*'), recursive=True)
        self.assertTrue(len(listdir(dir_to_test)))
        self.assertTrue(mocked_remove.called)

    @mock.patch('getpass.getpass')
    def test_get_password(self, getpw):
        getpw.return_value = 'pass'
        self.assertEqual(gpgdir.get_password(), 'pass')

    @mock.patch('gpgdir.get_home_dir')
    def test_decrypt_dir_not_exists(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertRaises(Exception, gpgdir.decrypt_dir, '/abc')

    @mock.patch('gpgdir.os.remove')
    @mock.patch('gpgdir.glob.glob')
    def test_decrypt_dir(self, mock_glob, mocked_remove):
        mock_glob.return_value = [
            os.path.join(dir_to_test, 'sub', 'test.txt'),
            os.path.join(dir_to_test, 'test.txt'),
            os.path.join(dir_to_test, 'test1.txt')
        ]
        gpgdir.encrypt_dir(dir_to_test)
        mock_glob.assert_called_with(os.path.join(dir_to_test, '**/*'), recursive=True)

        mock_glob.return_value = [
            os.path.join(dir_to_test, 'sub', 'test.txt.gpg'),
            os.path.join(dir_to_test, 'test.txt.gpg'),
            os.path.join(dir_to_test, 'test1.txt.gpg')
        ]
        gpgdir.decrypt_dir(dir_to_test)
        mock_glob.assert_called_with(os.path.join(dir_to_test, '**/*.gpg'), recursive=True)
        self.assertTrue(len(listdir(dir_to_test)))
        self.assertTrue(mocked_remove.called)

    @mock.patch('gpgdir.get_home_dir')
    def test_sign_dir_not_exists(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertRaises(Exception, gpgdir.sign_dir, '/abc')

    @mock.patch('gpgdir.glob.glob')
    def test_sign_dir(self, mock_glob):
        mock_glob.return_value = [
            os.path.join(dir_to_test, 'sub', 'test.txt'),
            os.path.join(dir_to_test, 'test.txt'),
            os.path.join(dir_to_test, 'test1.txt')
        ]
        gpgdir.encrypt_dir(dir_to_test)
        mock_glob.assert_called_with(os.path.join(dir_to_test, '**/*'), recursive=True)
        self.assertTrue(len(listdir(dir_to_test)))

    @mock.patch('gpgdir.get_home_dir')
    def test_verify_dir_not_exists(self, mock_get_home_dir):
        mock_get_home_dir.return_value = HOME_DIR
        self.assertRaises(Exception, gpgdir.sign_dir, '/abc')

    @mock.patch('gpgdir.glob.glob')
    def test_verify_dir(self, mock_glob):
        mock_glob.return_value = [
            os.path.join(dir_to_test, 'sub', 'test.txt.sig'),
            os.path.join(dir_to_test, 'test.txt.sig'),
            os.path.join(dir_to_test, 'test1.txt.sig')
        ]
        gpgdir.verify_dir(dir_to_test)
        mock_glob.assert_called_with(os.path.join(dir_to_test, '**/*'), recursive=True)
        self.assertTrue(len(listdir(dir_to_test)))


if __name__ == '__main__':
    unittest.main()
