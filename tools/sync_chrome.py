#!/usr/bin/env python3
"""Copy the shared header and footer (_partials/header.html and footer.html) into every page, between the markers

    <!-- CHROME:HEADER:START --> ... <!-- CHROME:HEADER:END -->      and      <!-- CHROME:FOOTER:START --> ... <!-- CHROME:FOOTER:END -->

and mark the link of the page itself in the menu (aria-current="page").  Run it after changing a partial:   python tools/sync_chrome.py
"""
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    header = read(os.path.join(ROOT, "_partials", "header.html")).rstrip("\n")
    footer = read(os.path.join(ROOT, "_partials", "footer.html")).rstrip("\n")
    changed = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(ROOT, name)
        text = read(path)
        if "<!-- CHROME:HEADER:START -->" not in text:
            print(f"skipped {name}: no markers")
            continue
        h = header
        if name != "404.html":                                                       # the link of this page is marked
            h = re.sub(r'(<a (?:class="nav-cta" )?href="%s")' % re.escape(name), r'\1 aria-current="page"', h)
        new = re.sub(r"<!-- CHROME:HEADER:START -->.*?<!-- CHROME:HEADER:END -->", lambda m: "<!-- CHROME:HEADER:START -->\n" + h + "\n<!-- CHROME:HEADER:END -->", text, flags=re.S)
        new = re.sub(r"<!-- CHROME:FOOTER:START -->.*?<!-- CHROME:FOOTER:END -->", lambda m: "<!-- CHROME:FOOTER:START -->\n" + footer + "\n<!-- CHROME:FOOTER:END -->", new, flags=re.S)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            changed += 1
            print("updated", name)
    print(f"{changed} page(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
