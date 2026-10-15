# Find duplicate files with a small Python tool

A tiny duplicate file finder built step by step. It compares what is inside files, not their names. It only reads. It never deletes, moves or changes a file.

## Run it

    python make_sample.py                # makes a practice folder called sample
    python dupfinder.py sample           # lists groups of identical files
    python dupfinder.py sample --min-size 0   # also counts empty files
    python -m unittest -v                # eight automated tests

On Windows, if `python` is not found, use `py` instead.

## Files

- `dupfinder.py` - the tool
- `make_sample.py` - makes made-up practice files
- `test_dupfinder.py` - tests
- `expected_output.txt` - the output the lesson shows; the automated check compares against it

## Notes

- Uses only what comes with Python 3. Tested on Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop, a network drive or a very large folder.
- The practice files are made up. Educational example, no warranty. Use at your own risk, and back up before deleting anything.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.
- The commands, with the real output recorded from a real run, are in the companion practice page: https://faiz12321.github.io/ai-tools-that-work/build-session-05-duplicate-finder.html . Nothing in it runs on your device.
