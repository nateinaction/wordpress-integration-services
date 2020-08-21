import main
import unittest


class TestUpdateDevelop(unittest.TestCase):
    def test_normalize_semver(self):
        version = '5.0'
        expect = '5.0.0'
        self.assertEqual(main.normalize_semver(version), expect)

        version = '5.0.1'
        expect = '5.0.1'
        self.assertEqual(main.normalize_semver(version), expect)


if __name__ == '__main__':
    unittest.main()
