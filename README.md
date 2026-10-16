# Find duplicate files with a small Python tool

Read-only teaching tool that groups files by size, hashes matching-size files,
then uses byte comparisons for matching hashes. It does not move or delete.
It does not decide which copy you should keep. Reports reveal file names.

## Practise

Save the three Python files in a new empty lesson folder. Python 3 is enough:

    python make_sample.py
    python dupfinder.py sample
    python dupfinder.py sample --min-size 0
    python -m unittest -v

Setup creates sample once, exclusively creates fictional practice files and
refuses any existing sample path. It never resets or replaces old data. Use a
different new empty folder rather than deleting existing data to force setup.

## Evidence and limits

11 tests use temporary fixtures, including setup file/folder collisions,
repeat-run refusal, nested unrelated data, byte contents and modification-time
preservation. A fixture hash clash confirms byte comparison separates different
contents. These fixture passes are not a universal safety proof.

The checker is unchanged in this setup repair. The lesson first shows a simple
fingerprint printer, then the final checker, then deliberately reproduces an
incorrect 128-byte test expectation. The full replacement test corrects this to
180 bytes. The recorder disables bytecode caching for these quick same-size
edits. Four recordings use unique temporary folders and preserve actual output,
including the intentionally failed traceback's temporary path. Paired platform
runs differ in those paths and unittest time. Displays use the first Windows
recording, not mixed output. No Windows desktop or macOS session was recorded.

Do not automate deletion from the report. Concurrent file changes, permission
errors, directory links, network filesystems and very large folders are not
fully covered. Keep private paths and reports private. expected_output.txt is
the stable sample report used by CI, not a full session transcript.

## License

MIT, see LICENSE. Python is separately licensed and not included.
