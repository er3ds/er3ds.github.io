#!/usr/bin/env python3
"""Check the website before it is uploaded:  python tools/check_site.py

  * every page: language, title, description, one h1, headings in order, every image with alt text, no duplicate ids
  * every link and image points to a file (and an anchor) that exists; nothing is loaded from another website (scripts, styles, images, fonts)
  * data/*.json are valid and have what the pages need (release.json: version, url, size, a 64-character SHA-256 that matches the file if it is in downloads/)
  * the text colors used on the blue and orange backgrounds have the contrast that WCAG asks for (4.5:1 for normal text)
  * no file is near the limits of GitHub (a warning above 50 MB; GitHub refuses 100 MB)
Exit code 1 if anything is wrong.
"""
import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
errors, warnings = [], []
pending = set()


def err(msg):
    errors.append(msg)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title = "", False
        self.lang, self.desc, self.og_image = None, None, None
        self.headings, self.ids, self.links, self.imgs, self.external = [], [], [], [], []
        self.stack = []

    VOID = {"meta", "link", "img", "br", "hr", "input", "source", "area", "base", "col", "embed", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.VOID:
            self.stack.append(tag)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "meta" and a.get("property") == "og:image":
            self.og_image = a.get("content")
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append((a.get("src", ""), a.get("alt")))
        for key in ("src", "href"):
            v = a.get(key, "")
            if re.match(r"(https?:)?//", v) and (tag in ("script", "img", "iframe", "source", "video", "audio") or (tag == "link" and a.get("rel") in ("stylesheet", "preload", "icon"))):
                self.external.append((tag, v))
        if tag in ("img", "script", "link", "source") and (a.get("src") or a.get("href")) and tag != "a":
            v = a.get("src") or a.get("href")
            if not re.match(r"(https?:)?//|data:|mailto:|#", v):
                self.links.append(v)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                err(f"unclosed <{self.stack.pop()}> before </{tag}>")
            self.stack.pop()
        else:
            err(f"stray </{tag}>")

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def luminance(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_pages():
    pages = {}
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        p = Page()
        with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
            p.feed(fh.read())
        for t in p.stack:
            err(f"{name}: <{t}> is never closed")
        pages[name] = p
    for name, p in pages.items():
        if p.lang != "en":
            err(f"{name}: <html lang> should be set (en)")
        if not p.title.strip():
            err(f"{name}: no <title>")
        if not p.desc:
            err(f"{name}: no meta description")
        if name != "404.html" and p.og_image is not None and not p.og_image.startswith("https://"):
            warnings.append(f"{name}: the preview image (og:image) has a relative address; link previews need a full one (run tools/set_site_url.py)")
        if p.headings.count(1) != 1:
            err(f"{name}: needs exactly one <h1> (has {p.headings.count(1)})")
        for prev, cur in zip(p.headings, p.headings[1:]):
            if cur > prev + 1:
                err(f"{name}: heading level jumps from h{prev} to h{cur}")
        dup = {i for i in p.ids if p.ids.count(i) > 1}
        if dup:
            err(f"{name}: duplicate ids {sorted(dup)}")
        for src, alt in p.imgs:
            if alt is None:
                err(f"{name}: image without alt attribute: {src}")
        for tag, url in p.external:
            err(f"{name}: loads <{tag}> from another website: {url}")
        for href in p.links:
            if re.match(r"(https?:)?//|mailto:|tel:|javascript:|data:", href):
                continue
            target, _, frag = href.partition("#")
            target = target.split("?")[0]
            path = os.path.join(ROOT, target) if target else os.path.join(ROOT, name)
            if target and not os.path.exists(path):
                if target.startswith("downloads/"):
                    pending.add(target)                                                  # (the download links are filled in by the page's script: reported once)
                else:
                    err(f"{name}: broken link {href}")
                continue
            if frag:
                other = pages.get(target or name)
                if other is not None and frag not in other.ids:
                    err(f"{name}: the anchor #{frag} is not in {target or name}")
    return pages


def check_json():
    def load(name):
        path = os.path.join(ROOT, "data", name)
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError) as exc:
            err(f"data/{name}: {exc}")
            return None
    site = load("site.json")
    if site is not None and not isinstance(site, dict):
        err("data/site.json must be an object")
    tut = load("tutorials.json")
    if tut is not None:
        items = tut.get("tutorials") if isinstance(tut, dict) else None
        if not isinstance(items, list):
            err('data/tutorials.json needs a list "tutorials"')
        else:
            for k, t in enumerate(items):
                if not t.get("title"):
                    err(f"data/tutorials.json: video {k + 1} has no title")
                yt, vid = t.get("youtube"), t.get("video")
                if not (yt or vid):
                    err(f'data/tutorials.json: video {k + 1} needs "youtube" (the id) or "video" (a file in videos/)')
                if vid and not os.path.exists(os.path.join(ROOT, vid)):
                    err(f"data/tutorials.json: the file {vid} does not exist")
    if isinstance(site, dict):
        repo, mode, mail = site.get("github_repo_url", ""), site.get("download_mode", ""), site.get("contact_email", "")
        if repo and not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?", repo):
            err('data/site.json: "github_repo_url" must look like https://github.com/OWNER/REPO')
        if mode not in ("", "github-release", "local"):
            err('data/site.json: "download_mode" must be "github-release" or "local"')
        if mail and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
            err('data/site.json: "contact_email" is not an e-mail address')
        if mode in ("", "github-release") and not repo:
            warnings.append('data/site.json: "github_repo_url" is empty, so the download page says the download is not set up yet (see the README)')
    rel_path = os.path.join(ROOT, "data", "release.json")
    rel = load("release.json") if os.path.exists(rel_path) else None
    if rel is None and isinstance(site, dict) and site.get("download_mode") == "local":
        err('data/site.json says "local" but data/release.json is missing (run tools/update_release.py)')
    if rel is not None:
        for key in ("version", "url", "size_bytes", "sha256", "date"):
            if key not in rel:
                err(f"data/release.json: missing {key}")
        if rel.get("sha256") and not re.fullmatch(r"[0-9a-f]{64}", rel["sha256"]):
            err("data/release.json: sha256 is not 64 hexadecimal characters")
        local = os.path.join(ROOT, rel.get("url", ""))
        if rel.get("url") and not re.match(r"https?://", rel["url"]):
            if not os.path.isfile(local):
                err(f"data/release.json: {rel['url']} does not exist")
            else:
                h = hashlib.sha256(open(local, "rb").read()).hexdigest()
                if h != rel.get("sha256"):
                    err("data/release.json: the SHA-256 does not match downloads/ (run tools/update_release.py again)")
                if os.path.getsize(local) != rel.get("size_bytes"):
                    err("data/release.json: the size does not match downloads/")


def check_contrast():
    css = open(os.path.join(ROOT, "assets", "css", "style.css"), encoding="utf-8").read()
    v = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css))
    navy, white = v["navy"], v["white"]
    pairs = [("text", v["ink"], white), ("muted text", v["muted"], white), ("muted text on soft", v["muted"], v["soft"]), ("link", v["blue-text"], white), ("link on sky", v["blue-text"], v["sky"]),
             ("heading on sky", navy, v["sky"]), ("button text", white, v["orange-deep"]), ("button hover", white, "#a43812"), ("orange text on pale", v["orange-deep"], v["orange-soft"]),
             ("code", navy, v["sky"]), ("header text", "#eaf1ff", "#0d1233"), ("hero text", "#dbe7ff", navy), ("hero text, lighter end", "#dbe7ff", "#1853ae"), ("hero small print", "#bcd0f5", navy),
             ("hero small print, lighter end", "#bcd0f5", "#1853ae"), ("eyebrow", "#ffb28f", navy), ("hero accent", "#ff9a73", navy), ("download facts label", "#aac2ef", "#163b86"),
             ("footer text", "#c9d8f5", "#0d1233"), ("footer fine print", "#9fb6e6", "#0d1233"), ("footer link", "#e6eeff", "#0d1233"), ("code block", "#e8f0ff", "#0b1f4a"), ("badge ok", "#17653a", "#e3f4e8"),
             ("pill", navy, v["sky"]), ("tab selected", navy, v["soft"]), ("tab idle", v["muted"], white)]
    for label, fg, bg in pairs:
        c = contrast(fg, bg)
        if c < 4.5:
            err(f"contrast {c:.2f}:1 is below 4.5:1 for {label} ({fg} on {bg})")
    return pairs


def check_sizes():
    for base, _, files in os.walk(ROOT):
        for f in files:
            path = os.path.join(base, f)
            size = os.path.getsize(path)
            rel = os.path.relpath(path, ROOT)
            if size > 95 * 1048576:
                err(f"{rel} is {size / 1048576:.0f} MB: GitHub refuses files above 100 MB")
            elif size > 50 * 1048576:
                warnings.append(f"{rel} is {size / 1048576:.0f} MB: GitHub warns above 50 MB")


def main():
    pages = check_pages()
    check_json()
    pairs = check_contrast()
    check_sizes()
    if pending:
        warnings.append("the pages link to " + ", ".join(sorted(pending)) + " as a fallback; with the default 'github-release' download these files are not needed (the script points the links at your release)")
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    n_links = sum(len(p.links) for p in pages.values())
    print(f"{len(pages)} pages, {n_links} links, {sum(len(p.imgs) for p in pages.values())} images, {len(pairs)} color pairs; {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
