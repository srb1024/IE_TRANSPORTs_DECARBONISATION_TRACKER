import re
import unittest
from pathlib import Path


class RepositoryStructureTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_required_directories_exist(self):
        required_dirs = [
            'data/raw',
            'data/interim',
            'data/processed',
            'data/dashboard_exports',
            'notebooks',
            'src/analytics/descriptive',
            'src/analytics/predictive',
            'src/analytics/prescriptive',
            'tests',
            'dashboard',
            'docs/figures',
        ]
        for rel in required_dirs:
            with self.subTest(path=rel):
                self.assertTrue((self.root / rel).is_dir())

    def test_required_files_exist(self):
        required_files = [
            'docs/data_dictionary.md',
            'docs/methodology.md',
            'requirements.txt',
            '.gitignore',
        ]
        for rel in required_files:
            with self.subTest(path=rel):
                self.assertTrue((self.root / rel).is_file())

    def test_notebooks_are_seven_and_numbered(self):
        notebook_paths = sorted((self.root / 'notebooks').glob('*.ipynb'))
        self.assertEqual(len(notebook_paths), 7)

        for notebook in notebook_paths:
            with self.subTest(notebook=notebook.name):
                self.assertRegex(notebook.name, re.compile(r'^\d{2}_.+\.ipynb$'))


if __name__ == '__main__':
    unittest.main()
