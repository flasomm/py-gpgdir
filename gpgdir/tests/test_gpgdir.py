from unittest import TestCase
import os
import gpgdir


class TestGpgDir(TestCase):
    def test_get_gpg_dir_ok(self):
        home = os.path.expanduser('~')
        expected_dir = gpgdir.get_gpg_dir()
        self.assertEqual(expected_dir, home + "/.gnupg")
