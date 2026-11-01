#!/usr/bin/env python3
"""Record a new release of the program for the download page: writes data/release.json (version, file name, size, SHA-256, date).

Two ways to offer the zip:

  A. In this repository (simplest; the default):
       python tools/update_release.py path/to/er3ds.zip [--manual path/to/ER3DS_manual.pdf]
     copies the files into downloads/ and records them.  Upload (commit) downloads/ and data/release.json.
     Every new zip adds its size (about 36 MB) to the repository's history.

  B. As a GitHub Release (keeps the repository small):  make a release on GitHub, attach er3ds.zip, then
       python tools/update_release.py path/to/er3ds.zip --url https://github.com/USER/REPO/releases/latest/download/er3ds.zip
     (add  --manual path/to/ER3DS_manual.pdf --manual-url https://github.com/USER/REPO/releases/latest/download/ER3DS_manual.pdf  for the manual).
     Nothing is copied; the download button points at the URL.  The URL with 'latest' always leads to the newest release.

The version is read from the zip itself (src/er3ds/__init__.py), so it cannot disagree with the file.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def version_of(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if re.search(r"(^|/)src/er3ds/__init__\.py$", n)]
        if not names:
            raise SystemExit(f"error: {zip_path} has no src/er3ds/__init__.py: is it the er3ds source zip?")
        m = re.search(r"__version__\s*=\s*[\"']([^\"']+)[\"']", z.read(names[0]).decode("utf-8", "replace"))
        if not m:
            raise SystemExit("error: no __version__ in src/er3ds/__init__.py")
        return m.group(1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", help="the er3ds source zip")
    ap.add_argument("--manual", help="the manual (PDF), optional")
    ap.add_argument("--url", help="where the zip is (a GitHub Release URL); then it is not copied into downloads/")
    ap.add_argument("--manual-url", help="where the manual is, with --url")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.zip):
        raise SystemExit(f"error: no such file: {a.zip}")
    version = version_of(a.zip)
    rel = dict(version=version, file="er3ds.zip", size_bytes=os.path.getsize(a.zip), sha256=sha256(a.zip),
               date=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    if a.url:
        rel["url"] = a.url
    else:
        os.makedirs(os.path.join(ROOT, "downloads"), exist_ok=True)
        shutil.copyfile(a.zip, os.path.join(ROOT, "downloads", "er3ds.zip"))
        rel["url"] = "downloads/er3ds.zip"
    if a.manual:
        if not os.path.isfile(a.manual):
            raise SystemExit(f"error: no such file: {a.manual}")
        man = dict(file="ER3DS_manual.pdf", size_bytes=os.path.getsize(a.manual))
        if a.manual_url:
            man["url"] = a.manual_url
        else:
            os.makedirs(os.path.join(ROOT, "downloads"), exist_ok=True)
            shutil.copyfile(a.manual, os.path.join(ROOT, "downloads", "ER3DS_manual.pdf"))
            man["url"] = "downloads/ER3DS_manual.pdf"
        rel["manual"] = man
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "release.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rel, fh, indent=2)
        fh.write("\n")
    print(f"version {version}, {rel['size_bytes'] / 1048576:.1f} MB, sha256 {rel['sha256'][:16]}...")
    print("wrote data/release.json" + ("" if a.url else "; copied the file(s) into downloads/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
