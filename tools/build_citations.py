#!/usr/bin/env python3
"""Write the list of citations of citations.html from the program's own list of references (src/er3ds/references.py), the one the program shows in its tabs and in `er3ds references`.

The page features the RECENT methods for the three kinds of method that matter for a citation: registration, parameterization and statistical analysis.  "Recent" is set in
tools/citations_config.json ("since": a year; "also_featured": the keys of older references you want in the main list anyway).  Every other reference of the program is still listed, in a
collapsed section at the end, so that nothing the program uses is hidden.

    python tools/build_citations.py                                  reads tools/references_snapshot.py (a copy of the program's references.py)
    python tools/build_citations.py --zip path/to/er3ds.zip          reads references.py out of the program's zip instead
    python tools/build_citations.py --source path/to/references.py
    python tools/build_citations.py --since 2005                     another cutoff, for this run only

Only the part of citations.html between  <!-- CITATIONS:START -->  and  <!-- CITATIONS:END -->  is replaced.  Nothing is added here that is not in the program's list: an entry that the
program marks as not checked online gets, as in the program, a search link and not a direct link, and is marked on the page.
"""
import argparse
import html
import json
import os
import re
import sys
import types
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HERE = os.path.dirname(os.path.abspath(__file__))

#: the kinds of method of the page: (id, heading, the first words of the program's tab titles that belong to it)
CATEGORIES = [("registration", "Registration methods", ("Registration", "Register New Shapes", "Geodesics")),
              ("parameterization", "Parameterization methods", ("Parameterization",)),
              ("statistics", "Statistical analysis methods", ("PCA", "Shape Clustering", "Shape Regression", "Time Models"))]


def load_references(source_text):
    mod = types.ModuleType("er3ds_references")
    sys.modules["er3ds_references"] = mod                      # (dataclasses looks its module up by name)
    exec(compile(source_text, "references.py", "exec"), mod.__dict__)
    return mod


def esc(text):
    return html.escape(text, quote=True)


def entry(r, used, titles):
    direct = bool(r.url)
    badges = (f'<span class="badge {"ok" if direct else "search"}">{"direct link" if direct else "search link"}</span>'
              + ("" if r.checked else '<span class="badge search">details not checked online</span>'))
    link = f'<a class="link" href="{esc(r.link)}" target="_blank" rel="noopener">{"Open the paper" if direct else "Search for it"}</a>'
    where = ", ".join(esc(titles[t]) for t in used.get(r.key, []))
    return (f'<li id="ref-{esc(r.key)}"><span class="tag">{esc(r.tag)}</span>: {esc(r.authors)} ({r.year}). {esc(r.title)}. {esc(r.venue)}. {link}{badges}'
            + (f'<div class="used">Used in: {where}</div>' if where else "") + '</li>')


def render(R, since, also):
    refs, used, titles = R.REFERENCES, R.used_by(), R.TOPIC_TITLES
    featured_keys = {k for k, r in refs.items() if r.year >= since or k in also}
    # the references of each kind of method, grouped as the program groups them (what each is used for)
    sections, in_a_category = [], set()
    for cid, heading, prefixes in CATEGORIES:
        groups = {}
        for topic, title in titles.items():
            if not title.startswith(prefixes):
                continue
            for what, rs in R.tab_references(topic):
                keep = [r for r in rs if r.key in featured_keys]
                if keep:
                    merged = groups.setdefault(what, [])
                    merged.extend(r for r in keep if r not in merged)
        sections.append((cid, heading, groups))
        in_a_category |= {r.key for rs in groups.values() for r in rs}
    featured = sorted((refs[k] for k in in_a_category), key=lambda r: r.tag.lower())
    older = sorted((r for r in refs.values() if r.key not in in_a_category), key=lambda r: r.tag.lower())
    count = lambda rs, f: sum(1 for r in rs if f(r))
    unchecked = [r for r in featured if not r.checked]
    plural = len(unchecked) != 1

    if unchecked:
        tail = (f'The other{"s" if plural else ""} {"are" if plural else "is"} marked on the page: {", ".join(esc(r.tag) for r in unchecked)} '
                f'{"were" if plural else "was"} written from the literature without that look-up, so {"they carry" if plural else "it carries"} a search link '
                f'(a bibliographic search by title and first author) and the details should be checked before you copy them into a paper.')
    else:
        tail = "All of them are marked as checked."
    out = ['<section>\n<div class="container narrow">', '<h2>Recent methods for registration, parameterization and statistical analysis</h2>',
           f'<p>ER3DS builds on recent work in elastic shape analysis. This page lists the methods from {since} on that the software uses for <strong>registration</strong>, <strong>parameterization</strong> '
           f'and <strong>statistical analysis</strong>, taken from the same reference list that the program shows in its tabs and prints with <code>er3ds references</code>. '
           f'If you use ER3DS in your work, please cite the papers of the methods you used.</p>',
           f'<div class="note"><p><strong>How far the entries have been checked.</strong> Of the {len(featured)} methods below, {count(featured, lambda r: r.checked)} were looked up online '
           f'(authors, title, journal and link) when the entry was written, and {count(featured, lambda r: r.url)} have a direct link. {tail}</p></div>',
           '<p>A citation for the software itself is not available yet; if you mention the program, give its name and the version number shown on the <a href="download.html">download page</a>.</p>',
           '<ul class="toc" aria-label="Jump to a part of the page">' + "".join(f'<li><a href="#{cid}">{esc(h)}</a></li>' for cid, h, g in sections if g)
           + '<li><a href="#references">All the references</a></li><li><a href="#older">Earlier methods</a></li></ul>', '</div>\n</section>']

    for k, (cid, heading, groups) in enumerate(sections):
        if not groups:
            continue
        out.append(f'<section id="{cid}"' + (' class="section-soft"' if k % 2 == 0 else "") + '>\n<div class="container narrow">')
        out.append(f'<h2>{esc(heading)}</h2>\n<ul class="what">')
        for what, rs in groups.items():
            out.append(f'<li><strong>{esc(what)}:</strong> ' + ", ".join(f'<a href="#ref-{esc(r.key)}">{esc(r.tag)}</a>' for r in rs) + '</li>')
        out.append('</ul>\n</div>\n</section>')

    out.append('<section id="references">\n<div class="container narrow">')
    out.append(f'<h2>The references <span class="muted small">({len(featured)}, A to Z)</span></h2>\n<ul class="cite-list">')
    out += [entry(r, used, titles) for r in featured]
    out.append('</ul>\n</div>\n</section>')

    out.append('<section class="section-soft" id="older">\n<div class="container narrow">')
    out.append(f'<h2>Earlier and classical methods <span class="muted small">({len(older)})</span></h2>')
    out.append(f'<p>The program also uses established tools from before {since}: classical statistics, optimization and mesh repair, and the foundations of some of the methods above. They are listed so that '
               f'nothing the program uses is hidden. Of these {len(older)}, {count(older, lambda r: r.checked)} were checked online; the others carry a search link and their details should be '
               f'checked before you cite them.</p>')
    out.append('<details><summary>Show the earlier references</summary>\n<ul class="cite-list">')
    out += [entry(r, used, titles) for r in older]
    out.append('</ul>\n</details>\n</div>\n</section>')
    stats = dict(featured=len(featured), featured_checked=count(featured, lambda r: r.checked), older=len(older), total=len(refs), unchecked=[r.tag for r in unchecked])
    return "\n".join(out), stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", help="the program's zip: read references.py from it")
    ap.add_argument("--source", default=os.path.join(HERE, "references_snapshot.py"), help="a references.py file (default: tools/references_snapshot.py)")
    ap.add_argument("--since", type=int, help="the first year of the 'recent' methods (default: tools/citations_config.json)")
    ap.add_argument("--page", default=os.path.join(ROOT, "citations.html"))
    a = ap.parse_args(argv)
    cfg = {}
    cfg_path = os.path.join(HERE, "citations_config.json")
    if os.path.isfile(cfg_path):
        with open(cfg_path, encoding="utf-8") as fh:
            cfg = json.load(fh)
    since = a.since or int(cfg.get("since", 2010))
    also = set(cfg.get("also_featured", []))
    if a.zip:
        with zipfile.ZipFile(a.zip) as z:
            names = [m for m in z.namelist() if re.search(r"(^|/)src/er3ds/references\.py$", m)]
            if not names:
                raise SystemExit(f"error: no src/er3ds/references.py in {a.zip}")
            text = z.read(names[0]).decode("utf-8")
    else:
        text = open(a.source, encoding="utf-8").read()
    R = load_references(text)
    unknown = sorted(k for k in also if k not in R.REFERENCES)
    if unknown:
        raise SystemExit("error: citations_config.json names references that do not exist: " + ", ".join(unknown))
    body, st = render(R, since, also)
    page = open(a.page, encoding="utf-8").read()
    new, k = re.subn(r"<!-- CITATIONS:START.*?-->.*?<!-- CITATIONS:END -->", lambda m: "<!-- CITATIONS:START (generated by tools/build_citations.py: do not edit by hand) -->\n" + body + "\n<!-- CITATIONS:END -->", page, flags=re.S)
    if k != 1:
        raise SystemExit("error: the markers CITATIONS:START / CITATIONS:END are not in " + a.page)
    with open(a.page, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    print(f"since {since}: {st['featured']} featured ({st['featured_checked']} checked online; not checked: {', '.join(st['unchecked']) or 'none'}), "
          f"{st['older']} earlier, {st['total']} in the program's list; written to {os.path.basename(a.page)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
