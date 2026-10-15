"""Creates a small, fixed folder of sample files for practising on.

Run: python make_sample.py
It makes a folder called sample/ next to this script. Safe to run twice.
"""
from pathlib import Path

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
    root = Path(root)
    for name, text in FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return len(FILES)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    count = make(here / "sample")
    print(f"Made {count} files in sample")
