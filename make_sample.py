"""Creates a small, fixed folder of sample files for practising on.

Run: python make_sample.py
It makes a folder called sample/ next to this script. Refuses any existing sample path. Never resets or replaces it.
"""
from pathlib import Path
import stat

FILES = {
    "holiday/beach.txt": "Beach day notes: sunscreen, towels, snacks.\n",
    "holiday/beach copy.txt": "Beach day notes: sunscreen, towels, snacks.\n",
    "holiday/packing.txt": "Packing list: passport, charger, hat.\n",
    "work/report-v1.txt": "Quarterly report draft.\nTotals to be checked.\n",
    "work/report-final.txt": "Quarterly report draft.\nTotals to be checked.\n",
    "work/report-final-OLD.txt": "Quarterly report draft.\nTotals to be checked.\n",
    "work/notes.txt": "Call the supplier on Monday.\n",
    "downloads/readme.txt": "Beach day notes: sunscreen, towels, snacks.\n",
    "downloads/same-size-different.txt": "Beach day notes: sunscreen, towels, snackz.\n",
    "downloads/empty1.txt": "",
    "downloads/empty2.txt": "",
}


def make(root):
    root = Path(root).absolute()
    if '..' in root.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for parent in reversed(root.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Linked/reparse parents are unsupported.')
    root.mkdir()  # Atomic refusal if any file, folder or link already exists.
    for name, text in FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(text.encode("utf-8"))
    return len(FILES)


if __name__ == "__main__":
    here = Path(__file__).absolute().parent
    try:
        count = make(here / "sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print(f"Made {count} files in sample")
