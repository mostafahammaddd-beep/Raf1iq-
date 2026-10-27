import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.verify_record_dependencies import validate_graph  # noqa: E402


class RecordDependencyCompatibilityTests(unittest.TestCase):
    def test_pubspec_and_workflow_include_the_compatibility_fix(self):
        pubspec = (ROOT / "pubspec.yaml").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "android_build.yml").read_text(encoding="utf-8")
        self.assertIn("record: ^6.2.1", pubspec)
        self.assertIn("scripts/verify_record_dependencies.py", workflow)
        self.assertIn("flutter pub deps --json", workflow)

    def test_accepts_compatible_record_6_graph(self):
        graph = {
            "packages": [
                {"name": "record", "version": "6.2.1"},
                {"name": "record_linux", "version": "1.3.1"},
                {"name": "record_platform_interface", "version": "1.6.0"},
            ]
        }
        self.assertEqual(validate_graph(graph), [])

    def test_rejects_original_incompatible_graph(self):
        graph = {
            "packages": [
                {"name": "record", "version": "5.2.1"},
                {"name": "record_linux", "version": "0.7.2"},
                {"name": "record_platform_interface", "version": "1.6.0"},
            ]
        }
        errors = validate_graph(graph)
        self.assertTrue(errors)
        self.assertTrue(any("record_linux=0.7.2" in error for error in errors))

    def test_rejects_missing_packages(self):
        self.assertTrue(validate_graph({"packages": []}))

    def test_rejects_invalid_version_format(self):
        graph = {
            "packages": [
                {"name": "record", "version": "future"},
                {"name": "record_linux", "version": "1.3.1"},
                {"name": "record_platform_interface", "version": "1.6.0"},
            ]
        }
        self.assertTrue(any("cannot validate record=future" in error for error in validate_graph(graph)))


if __name__ == "__main__":
    unittest.main()
