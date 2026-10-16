# Find duplicate files with a small Python tool

The final checker groups by size, SHA-256 and uncached chunked byte comparison. It has no write, move, delete or network code. Reports show relative file paths and extra logical file bytes, not guaranteed recoverable physical space. Do not automate deletion.

## Practice

Save the three Python files in a NEW empty local lesson folder. Python 3.10+ is enough.

    python make_sample.py
    python dupfinder.py sample
    python dupfinder.py sample --min-size 0
    python -m unittest -v

Two Windows and two Ubuntu replays use the exact visible code, including the intentional wrong 128-byte assertion followed by the full corrected 180-byte test replacement. Final test suite is 25 tests, with one Unix-pipe skip on Windows. Symlink tests execute on these recording runners but can skip where unavailable. Both pairs differ in temporary traceback paths and unittest timings; first Windows stdout is displayed, not mixed or rewritten.
Setup exclusively creates a NEW fictional sample and refuses existing, traversal and linked/reparse-point ancestor paths. No reset/delete. Final checker refuses unsafe input/ancestor/tree links, reparse points, multiply linked files, special entries and traversal. It caps traversal at 10000 entries, but reading files/listing directories still uses memory/time and is not a resource sandbox. Stop editors and sync. This is a best-effort preflight, not hostile-race protection.
Enumeration/metadata/comparison failures return exit 2 rather than false clean. Hash-read failures produce a visibly incomplete report and nonzero exit. Final byte comparison is chunked and uncached: the regression test catches stale filecmp-style cached comparisons after a same-size edit with restored modification time. Files can still change during a scan; no atomic snapshot is promised.
The report sums extra logical file bytes. It does not measure physical blocks, compression, sparse files, deduplication or guaranteed recoverable disk space. No deletion recommendation follows from a duplicate group; deciding which file to keep stays yours. Read-only refers to this script's lack of write/move/delete/network code, not the whole OS or sync software. Report paths can be private. Tests use small temporary fixtures, not real user trees or desktop Windows/macOS.
The first fingerprint-printer prototype is for the fictional sample only. It is not the final safe-path checker. The full final file replaces it before the duplicate report/tests. The recorder disables bytecode caching while editing same-sized source files quickly and removes only its own temporary fixture workspace.

MIT code. Python has separate terms and is not included.

## Paired recordings

- Windows: https://github.com/faiz12321/lesson-lab/actions/runs/38965897753
- Ubuntu: https://github.com/faiz12321/lesson-lab/actions/runs/38966031435

Python filesystem reference: https://docs.python.org/3/library/os.html
