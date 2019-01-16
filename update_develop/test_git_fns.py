import main
import shutil
import subprocess
import tempfile
import unittest

class TestGitFns(unittest.TestCase):
    def setUp(self):
        self.bare_repo_dir = tempfile.mkdtemp()
        self.bare_repo_file_url = 'file://{}'.format(self.bare_repo_dir)
        self.original_repo_dir = tempfile.mkdtemp()
        self.cloned_repo_dir = tempfile.mkdtemp()
        self.branch = 'develop'
        self.test_file = 'test.txt'

        # Initialize the bare repo
        subprocess.run(['git', 'init', '--bare', self.bare_repo_dir], capture_output=True)

        # Create first commit to repo
        subprocess.run(['git', 'clone', self.bare_repo_file_url, self.original_repo_dir], capture_output=True)
        # Create test file
        with open('{}/{}'.format(self.original_repo_dir, self.test_file), "w") as test_file:
            subprocess.run(['echo', '-n', 'Hello world!'], cwd=self.original_repo_dir, stdout=test_file)
        subprocess.run(['git', 'add', '.'], cwd=self.original_repo_dir)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.original_repo_dir, capture_output=True)
        # Create the develop branch
        subprocess.run(['git', 'checkout', '-b', self.branch], cwd=self.original_repo_dir, capture_output=True)
        # Push to bare repo
        subprocess.run(['git', 'push', 'origin', self.branch], cwd=self.original_repo_dir, capture_output=True)
    
    def tearDown(self):
        shutil.rmtree(self.bare_repo_dir, ignore_errors=True)
        shutil.rmtree(self.original_repo_dir, ignore_errors=True)
        shutil.rmtree(self.cloned_repo_dir, ignore_errors=True)

    def test_git_fns(self):
        # Verify test file is setup correctly
        cat_test_txt = subprocess.run(['cat', self.test_file], cwd=self.original_repo_dir, capture_output=True)
        self.assertEqual(cat_test_txt.stdout.decode('utf8'), 'Hello world!')
        
        # Verify cloned repo only has develop branch
        main.git_clone(self.bare_repo_file_url, self.branch, self.cloned_repo_dir)
        check_cloned_branch = subprocess.run(['git', 'branch'], cwd=self.cloned_repo_dir, capture_output=True)
        self.assertEqual(check_cloned_branch.stdout.decode('utf8'), '* {}\n'.format(self.branch))

        # Modify test file
        new_test_file_content = '!Hola mundo!'
        with open('{}/{}'.format(self.cloned_repo_dir, self.test_file), "w") as test_file:
            subprocess.run(['echo', '-n', new_test_file_content], cwd=self.cloned_repo_dir, stdout=test_file)
        main.git_add_commit_and_push('Test commit', self.branch, self.cloned_repo_dir)

        # Verify test file was modified in bare repo
        subprocess.run(['git', 'pull', 'origin', self.branch], cwd=self.original_repo_dir, capture_output=True)
        cat_test_txt = subprocess.run(['cat', self.test_file], cwd=self.original_repo_dir, capture_output=True)
        self.assertEqual(cat_test_txt.stdout.decode('utf8'), new_test_file_content)


if __name__ == '__main__':
    unittest.main()