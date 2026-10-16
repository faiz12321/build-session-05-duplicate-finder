import tempfile
import unittest
from pathlib import Path
from unittest import mock

import dupfinder
import make_sample


class DupFinderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "sample"
        make_sample.make(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def names(self, groups):
        return [[p.relative_to(self.root).as_posix() for p in g[1]] for g in groups]

    def test_finds_the_two_groups(self):
        groups, skipped = dupfinder.find_duplicates(self.root)
        self.assertEqual(len(groups), 2)
        self.assertEqual(skipped, [])

    def test_same_size_different_content_is_not_a_duplicate(self):
        groups, _ = dupfinder.find_duplicates(self.root)
        flat = sum(self.names(groups), [])
        self.assertNotIn("downloads/same-size-different.txt", flat)

    def test_renamed_copy_is_found(self):
        groups, _ = dupfinder.find_duplicates(self.root)
        flat = sum(self.names(groups), [])
        self.assertIn("work/report-final-OLD.txt", flat)

    def test_empty_files_ignored_by_default_and_counted_when_asked(self):
        groups, _ = dupfinder.find_duplicates(self.root)
        self.assertNotIn("downloads/empty1.txt", sum(self.names(groups), []))
        groups, _ = dupfinder.find_duplicates(self.root, min_size=0)
        self.assertIn("downloads/empty1.txt", sum(self.names(groups), []))

    def snapshot(self):
        return sorted((p.relative_to(self.root).as_posix(), p.is_dir(),
                       p.stat().st_mtime_ns,
                       p.read_bytes() if p.is_file() else None)
                      for p in self.root.rglob("*"))

    def test_never_changes_the_files(self):
        before = self.snapshot()
        dupfinder.find_duplicates(self.root)
        self.assertEqual(before, self.snapshot())

    def test_setup_refuses_existing_folder_and_keeps_nested_user_data(self):
        nested = self.root / "unrelated" / "deep.txt"
        nested.parent.mkdir(); nested.write_bytes(b"KEEP")
        before = self.snapshot()
        with self.assertRaises(FileExistsError):
            make_sample.make(self.root)
        self.assertEqual(before, self.snapshot())

    def test_setup_refuses_file_path(self):
        path = Path(self.tmp.name) / "file"
        path.write_bytes(b"KEEP")
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        with self.assertRaises(FileExistsError):
            make_sample.make(path)
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))

    def test_setup_cli_repeat_refuses(self):
        import shutil, subprocess, sys
        script = Path(self.tmp.name) / "make_sample.py"
        shutil.copyfile(Path(make_sample.__file__), script)
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Nothing was replaced or deleted", result.stderr)
        self.assertEqual(before, self.snapshot())

    def test_missing_folder_is_a_clear_error(self):
        with self.assertRaises(NotADirectoryError):
            dupfinder.find_duplicates(self.root / "nope")

    def test_wasted_space_in_report(self):
        groups, skipped = dupfinder.find_duplicates(self.root)
        text = dupfinder.report(self.root, groups, skipped)
        self.assertIn("2 group(s) of duplicates. Extra copies use 180 bytes.", text)

    def test_a_fingerprint_clash_is_not_enough(self):
        # Pretend every file has the same fingerprint. The byte check must still
        # keep different files apart, so the tool never calls them copies.
        with mock.patch.object(dupfinder, "file_hash", return_value="same"):
            groups, _ = dupfinder.find_duplicates(self.root)
        flat = sum(self.names(groups), [])
        self.assertNotIn("downloads/same-size-different.txt", flat)
        self.assertEqual(len(groups), 2)


if __name__ == "__main__":
    unittest.main()
