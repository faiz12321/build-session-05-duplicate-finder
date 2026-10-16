"""Find duplicate files in a folder. It only reads. It never deletes or moves anything.

Run: python dupfinder.py FOLDER [--min-size BYTES]
"""
import os
import stat
import hashlib
import sys
from collections import defaultdict
from pathlib import Path


def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path


def list_files(folder):
    """Refuse unsupported paths and propagate traversal errors, with an entry cap."""
    # Keep the prior missing-folder API shape for this teaching example.
    if not Path(folder).exists():
        raise NotADirectoryError(f'Not a folder: {folder}')
    root = safe_input(folder, directory=True)
    found = []
    stack = [root]
    count = 0
    while stack:
        current = safe_input(stack.pop(), directory=True)
        with os.scandir(current) as entries:
            ordered = sorted(entries, key=lambda entry: entry.name)
        for entry in ordered:
            count += 1
            if count > 10000:
                raise OSError('More than 10000 entries; refusing this tree.')
            info = entry.stat(follow_symlinks=False)
            directory = stat.S_ISDIR(info.st_mode)
            child = safe_input(entry.path, directory=directory)
            if directory:
                stack.append(child)
            else:
                found.append(child)
    return sorted(found)


def file_hash(path, chunk=1024 * 1024):
    """SHA-256 of the file contents, read in chunks; this is not a resource sandbox."""
    digest = hashlib.sha256()
    with open(safe_input(path), "rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def same_bytes(first, second):
    """True only if the two files are identical byte for byte."""
    with safe_input(first).open('rb') as a, safe_input(second).open('rb') as b:
        while True:
            left, right = a.read(1024 * 1024), b.read(1024 * 1024)
            if left != right:
                return False
            if not left:
                return True


def confirm_groups(paths):
    """Split paths that share a fingerprint into groups that really match byte for byte.

    A matching SHA-256 is very strong evidence, but this is the final check.
    """
    clusters = []
    for path in paths:
        for cluster in clusters:
            if same_bytes(cluster[0], path):
                cluster.append(path)
                break
        else:
            clusters.append([path])
    return clusters


def find_duplicates(folder, min_size=1):
    """Return (groups, skipped). A group is a list of paths with identical contents.

    Files are grouped by size first, because files of different sizes cannot be
    identical. Only files that share a size are hashed. Files that share a
    fingerprint are then compared byte for byte before they count as copies.
    """
    by_size = defaultdict(list)
    for path in list_files(folder):
        size = safe_input(path).stat().st_size
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
        for same_hash in by_hash.values():
            if len(same_hash) < 2:
                continue
            for same in confirm_groups(same_hash):
                if len(same) > 1:
                    groups.append((size, sorted(same)))
    groups.sort(key=lambda g: (-g[0], g[1][0]))
    return groups, sorted(skipped)


def report(folder, groups, skipped):
    root = Path(folder).absolute()
    lines = ["Incomplete report: some candidate files could not be read."] if skipped else []
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
    except OSError as error:
        print(error)
        return 2
    print(report(args[0], groups, skipped))
    return 2 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
