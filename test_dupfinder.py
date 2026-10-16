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


class PathSafety(unittest.TestCase):
    def setUp(self):
        import os
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base/'sample'
        make_sample.make(self.root)
    def link(self, path, target, directory=False):
        try: path.symlink_to(target, target_is_directory=directory)
        except OSError: self.skipTest('Symlink creation unavailable')
    def test_file_link(self):
        self.link(self.root/'linked', self.root/'work'/'notes.txt')
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_directory_loop(self):
        self.link(self.root/'loop', self.root, True)
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_dangling_link(self):
        self.link(self.root/'linked', self.root/'missing')
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_linked_parent(self):
        self.link(self.base/'linked', self.root, True)
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.base/'linked'/'work')
    def test_hardlink(self):
        import os
        os.link(self.root/'work'/'notes.txt', self.root/'hard')
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_pipe(self):
        import os
        if not hasattr(os,'mkfifo'): self.skipTest('Unix pipe unavailable')
        os.mkfifo(self.root/'pipe')
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_traversal(self):
        with self.assertRaises(OSError): dupfinder.find_duplicates(self.root/'..'/'sample')
    def test_enumeration_error(self):
        with mock.patch('os.scandir', side_effect=OSError('forced error')):
            with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
            self.assertEqual(dupfinder.main([str(self.root)]),2)
    def test_metadata_failure_not_silently_skipped(self):
        real = dupfinder.safe_input
        def fail(path,*args,**kwargs):
            if str(path).endswith('notes.txt'): raise OSError('forced metadata error')
            return real(path,*args,**kwargs)
        with mock.patch.object(dupfinder,'safe_input',side_effect=fail):
            with self.assertRaises(OSError): dupfinder.find_duplicates(self.root)
    def test_comparison_is_not_cached(self):
        a=self.base/'a';b=self.base/'b';a.write_bytes(b'aa');b.write_bytes(b'aa')
        self.assertTrue(dupfinder.same_bytes(a,b))
        import os
        old=b.stat();b.write_bytes(b'bb');os.utime(b,ns=(old.st_atime_ns,old.st_mtime_ns))
        self.assertFalse(dupfinder.same_bytes(a,b))
    def test_setup_linked_parent(self):
        self.link(self.base/'linked',self.root,True)
        with self.assertRaises(OSError):make_sample.make(self.base/'linked'/'new')
    def test_setup_traversal(self):
        with self.assertRaises(OSError):make_sample.make(self.root/'..'/'new')

    def test_hash_failure_is_incomplete_nonzero(self):
        with mock.patch.object(dupfinder, 'file_hash', side_effect=OSError('forced read failure')):
            groups, skipped = dupfinder.find_duplicates(self.root)
            self.assertTrue(skipped)
            self.assertIn('Incomplete report',dupfinder.report(self.root,groups,skipped))
            self.assertEqual(dupfinder.main([str(self.root)]),2)
    def test_byte_comparison_failure_is_nonzero(self):
        with mock.patch.object(dupfinder, 'same_bytes', side_effect=OSError('forced compare failure')):
            self.assertEqual(dupfinder.main([str(self.root)]),2)


if __name__ == "__main__":
    unittest.main()
