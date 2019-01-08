import main
import shutil
import subprocess
import tempfile
import unittest

class TestGitFns(unittest.TestCase):
    def setUp(self):
        self.original_repo_dir = tempfile.mkdtemp()
        self.cloned_repo_dir = tempfile.mkdtemp()
        self.branch = 'develop'

        # Initialize the repo
        subprocess.run(['git', 'init', self.original_repo_dir])
        #subprocess.run(['git', 'branch', self.branch], cwd=self.original_repo_dir)
        with open('test.txt', "w") as outfile:
            subprocess.run(['echo', 'Hello world!'], cwd=self.original_repo_dir, stdout=outfile)
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Initial commit'])

    
    def tearDown(self):
        shutil.rmtree(self.original_repo_dir, ignore_errors=True)
        shutil.rmtree(self.cloned_repo_dir, ignore_errors=True)

    def test_git_fns(self):
        # Verify test file is setup correctly
        cat_test_txt = subprocess.run(['ls', '-la'], cwd=self.original_repo_dir, capture_output=True)
        self.assertEqual(cat_test_txt.stdout.decode('utf8'), 'Hello world!')

        main.git_clone(self.original_repo_dir, self.branch)


if __name__ == '__main__':
    unittest.main()