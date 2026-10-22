"""Regression checks for the invalid hand-zipped VSIX and duplicate paths."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
import zipfile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from package_vsix import validate_layout


class VsixPackagingRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (BASE / '.scratch').mkdir(exist_ok=True)

    def test_old_zip_with_only_xml_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=BASE / '.scratch', ignore_cleanup_errors=True) as directory:
            package = Path(directory) / 'old.vsix'
            with zipfile.ZipFile(package, 'w') as archive:
                archive.writestr('extension.vsixmanifest', '<PackageManifest/>')
                archive.writestr('[Content_Types].xml', '<Types/>')
            with self.assertRaisesRegex(ValueError, 'catalog.json'):
                validate_layout(package)

    def test_sdk_payload_must_keep_exact_relative_paths(self):
        with tempfile.TemporaryDirectory(dir=BASE / '.scratch', ignore_cleanup_errors=True) as directory:
            package = Path(directory) / 'bad-prefix.vsix'
            with zipfile.ZipFile(package, 'w') as archive:
                for filename in ('manifest.json', 'catalog.json'):
                    archive.writestr(filename, json.dumps({}))
                archive.writestr('extension.vsixmanifest', '<PackageManifest/>')
                archive.writestr('[Content_Types].xml', '<Types/>')
                archive.writestr('runtime/examples/runtime/examples/banker.cpp', '// wrong path')
            with self.assertRaisesRegex(ValueError, 'Missing VSIX payload'):
                validate_layout(package, ['runtime/examples/banker.cpp'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
