"""Find duplicate files in a folder. It only reads. It never deletes or moves anything.

Run: python dupfinder.py FOLDER [--min-size BYTES]
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path


def list_files(folder):
    """Every regular file under folder, in a stable order."""
    root = Path(folder)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    return sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink())


def file_hash(path, chunk=1024 * 1024):
    """SHA-256 of the file contents, read in chunks so big files are fine."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def find_duplicates(folder, min_size=1):
    """Return (groups, skipped). A group is a list of paths with identical contents.

    Files are grouped by size first, because files of different sizes cannot be
    identical. Only files that share a size are hashed.
    """
    by_size = defaultdict(list)
    for path in list_files(folder):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size >= min_size:
            by_size[size].append(path)

    groups = []
    skipped = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for path in paths:
            try:
                by_hash[file_hash(path)].append(path)
            except OSError as error:
                skipped.append((path, error.strerror or str(error)))
        for same in by_hash.values():
            if len(same) > 1:
                groups.append((size, sorted(same)))
    groups.sort(key=lambda g: (-g[0], g[1][0]))
    return groups, sorted(skipped)


def report(folder, groups, skipped):
    root = Path(folder)
    lines = []
    wasted = 0
    for number, (size, paths) in enumerate(groups, start=1):
        wasted += size * (len(paths) - 1)
        lines.append(f"Group {number}: {len(paths)} files, {size} bytes each")
        for path in paths:
            lines.append("  " + path.relative_to(root).as_posix())
    for path, reason in skipped:
        lines.append(f"Could not read: {path.relative_to(root).as_posix()} ({reason})")
    lines.append(f"{len(groups)} group(s) of duplicates. Extra copies use {wasted} bytes.")
    return "\n".join(lines)


def main(argv):
    args = list(argv)
    min_size = 1
    if "--min-size" in args:
        at = args.index("--min-size")
        try:
            min_size = int(args[at + 1])
        except (IndexError, ValueError):
            print("--min-size needs a whole number of bytes.")
            return 2
        del args[at:at + 2]
    if len(args) != 1:
        print("Usage: python dupfinder.py FOLDER [--min-size BYTES]")
        return 2
    try:
        groups, skipped = find_duplicates(args[0], min_size)
    except NotADirectoryError as error:
        print(error)
        return 2
    print(report(args[0], groups, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
