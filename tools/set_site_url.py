#!/usr/bin/env python3
"""Tell the site its GitHub repository, and write the web address of the site into the pages' preview tags (og:image, og:url): link previews (when somebody shares the address in a message, a
social network or a chat) need a FULL address, not a relative one.  Run it once, and again if you ever rename the organization or the repository:

    python tools/set_site_url.py https://github.com/er3ds/er3ds            ->  https://er3ds.github.io/er3ds/
    python tools/set_site_url.py https://github.com/er3ds/er3ds.github.io  ->  https://er3ds.github.io/
    python tools/set_site_url.py https://github.com/er3ds/er3ds --site-url https://www.mydomain.org/     (if you use your own domain)

It also writes data/site.json ("github_repo_url").  Then upload data/site.json and the pages (*.html).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def pages_url(repo_url):
    m = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?", repo_url)
    if not m:
        raise SystemExit("error: the repository address must look like https://github.com/OWNER/REPO")
    owner, name = m.group(1), m.group(2)
    host = f"https://{owner.lower()}.github.io/"
    return host if name.lower() == f"{owner.lower()}.github.io" else host + name + "/"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="the address of the repository, https://github.com/OWNER/REPO")
    ap.add_argument("--site-url", help="the address of the site, if it is not the GitHub Pages one (a custom domain)")
    a = ap.parse_args(argv)
    repo = a.repo.rstrip("/")
    site_url = (a.site_url or pages_url(repo)).rstrip("/") + "/"
    path = os.path.join(ROOT, "data", "site.json")
    with open(path, encoding="utf-8") as fh:
        site = json.load(fh)
    site["github_repo_url"] = repo
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(site, fh, indent=2)
        fh.write("\n")
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(ROOT, name)
        text = open(p, encoding="utf-8").read()
        new = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{site_url}assets/img/og-image.png">', text)
        page = "" if name == "index.html" else name
        new = re.sub(r'<meta property="og:url" content="[^"]*">\n?', "", new)
        new = new.replace('<meta property="og:image"', f'<meta property="og:url" content="{site_url}{page}">\n<meta property="og:image"', 1)
        if new != text:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            n += 1
    print(f"repository {repo}\nsite address {site_url}\nupdated data/site.json and {n} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
