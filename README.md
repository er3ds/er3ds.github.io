# The ER3DS website

A static website (plain HTML, CSS and JavaScript, nothing to build and nothing loaded from other websites) for **GitHub Pages**:
a home page, **Download and install**, **Workflow** (the steps of a shape analysis, with pictures), **Video tutorials** and **Citations**.

You publish it by uploading these files to a GitHub repository and switching on GitHub Pages. You publish a new version of the software by attaching its zip to a *release*: the download page then shows the new version by itself.

## 1. Your setup

* **Organization:** `er3ds` (a free GitHub organization, created from your own account: no second account and no new e-mail address). **Repository:** `er3ds`, **public** (GitHub Pages needs a public repository on the free plan).
* **The web address of the site is then `https://er3ds.github.io/er3ds/`.** GitHub builds it from the owner's name and the repository's name. If you would rather have the shorter **`https://er3ds.github.io/`**, name the repository **`er3ds.github.io`** instead (or rename it later, see section 7).
* `data/site.json` is already filled in with `https://github.com/er3ds/er3ds` and the contact address; the preview tags of the pages already carry the address above.
* The contact address is shown on the site as a link in the footer, so it is **public**; anybody can read it, and automatic address-collectors may find it. Remove `contact_email` from `data/site.json` to hide it, or use a project address instead.
* There is **no license** line on the site, as you decided. (Without a license, others have no stated permission to copy or redistribute the software; you can add one later in `license_note` and in a `LICENSE` file.)

## 2. Publish the site (in the browser)

1. In the account (or organization) click **New repository**: name as in the table, **Public**, tick "Add a README" if you like.
2. **Add file, Upload files**: drag the *contents* of this folder into the page (the files and the folders `assets`, `data`, `tools`, `downloads`, `videos`, not a folder around them) and **Commit changes**. (Browser uploads accept files up to 25 MB; the site itself is a few MB. Dragging whole folders works in the usual browsers; if yours refuses, use GitHub Desktop.)
3. **Settings, Pages**: under *Build and deployment* choose **Deploy from a branch**, branch **main**, folder **/ (root)**, **Save**. After a minute or two the address appears at the top of that page.
4. `data/site.json` is already filled in (your repository and the contact address). Check that the repository address in it is exactly the one you created; if you named the repository differently, run `python tools/set_site_url.py https://github.com/OWNER/REPO` (or edit `github_repo_url` in the browser).

## 3. Offer the software (a release)

The zip is about 34 MB, more than a browser upload to the repository accepts, so it is attached to a **release** (releases accept files up to 2 GB):

1. In the repository: **Releases**, **Create a new release**.
2. **Tag**: the version, for example `v0.6.0`. **Title**: for example `ER3DS 0.6.0`.
3. Attach **`er3ds.zip`** and, if you like, **`ER3DS_manual.pdf`**. *The file names must be exactly these.* **Publish release**.

The download page asks GitHub for the **latest release** and shows its version (from the tag), date and size, and its Download button points at the zip. If GitHub shows a SHA-256 for the file, the page shows it too. **To publish a new version: make a new release with the same two file names. Nothing else has to be changed or uploaded.** Until the first release exists, the button leads to the releases page.

If a visitor's network or GitHub's limit for anonymous requests stops the page from asking, the button still works (it points at `releases/latest/download/er3ds.zip`), only the version, date and size are left out: the page never shows a number it does not know.

## 4. Things you will want to change

| What | Where |
|---|---|
| Your repository, a contact address, a license line | `data/site.json` |
| Video tutorials | `data/tutorials.json` (below) |
| Which citations are featured | `tools/citations_config.json`, then rebuild the page (below) |
| The wording of a page | the `.html` file (the text is plain HTML) |
| The header or footer of all pages | `_partials/header.html` or `footer.html`, then `python tools/sync_chrome.py` |

### Video tutorials
Add entries to `data/tutorials.json`; the page builds its cards from the list, and the "Coming soon" boxes disappear as soon as there is one:

```json
{
  "tutorials": [
    { "title": "Installing ER3DS", "level": "Beginner", "duration": "6 min",
      "description": "From the download to the first window.", "youtube": "VIDEO_ID" },
    { "title": "A first analysis", "video": "videos/first-analysis.mp4" }
  ]
}
```
`youtube` is the 11-character id from the video's address. The visitor's browser contacts YouTube only after the play button is clicked (the privacy-enhanced player is used). `video` is a file in `videos/` (.mp4 or .webm; a browser upload takes up to 25 MB per file, so longer videos are better on YouTube).

### Citations
The page lists the **recent methods for registration, parameterization and statistical analysis** (from the year in `tools/citations_config.json`, 2010 at present), and the earlier ones in a collapsed section. To change what is featured, edit that file (`since`, or the keys of older references in `also_featured`) and run, on a computer with Python:

```
python tools/build_citations.py
```

then upload the new `citations.html`. The list comes from the program's own references (`tools/references_snapshot.py` is a copy of `src/er3ds/references.py`; after a new version of the program, refresh it with `python tools/build_citations.py --zip path/to/er3ds.zip`). Entries that the program marks as not checked online are marked on the page too: please check them before you rely on them.

## 5. Before you announce it (a checklist)

* **License and authors.** The program's `pyproject.toml` still says to add them before publishing; the site does not invent any. Decide, and put a line in `license_note`.
* **The install notes** say the installation was tested on Linux only; the page says so. Change it when someone has tested Windows and macOS.
* **The tutorial placeholders** ("Coming soon", and the sentence that tutorials are being prepared) are yours to edit in `tutorials.html`.
* Run `python tools/check_site.py`: it tests every link, every image's alt text, the headings, the color contrast, the data files and the file sizes.

## 6. Another way to offer the zip: a file of the site

If you prefer the zip to be a file of the repository, set `"download_mode": "local"` in `data/site.json` and run, after each new version,

```
python tools/update_release.py path/to/er3ds.zip --manual path/to/ER3DS_manual.pdf
```

which copies the files into `downloads/` and writes `data/release.json` (version read from the zip, size, SHA-256). Then upload `downloads/` and `data/`. A file above 25 MB cannot be uploaded in the browser: use GitHub Desktop or git. Every new zip adds its size to the history of the repository, which is why the release way is the default.

## 7. If you rename the organization or the repository later

This is easy for the site, and takes minutes:

1. Rename on GitHub (Settings, General, *Repository name*; for an organization, Settings, *Organization name*).
2. Tell the site: `python tools/set_site_url.py https://github.com/NEWOWNER/NEWREPO` (it rewrites `data/site.json` and the preview addresses in the pages), then upload `data/site.json` and the `.html` files. Without Python you can edit `github_repo_url` in `data/site.json` in the browser; the only thing that stays old is the address inside the link-preview tags.
3. **What GitHub does with the old name.** It redirects most links to a renamed repository (its page, its release downloads, its git address), but **the address of the website changes at once** (the old `github.io` address stops working), and the old name becomes free for anybody to take, which ends the redirects. So tell people the new address, and check GitHub's documentation on renaming before you do it.
4. Releases and their files are kept; nothing has to be re-uploaded.

Renaming **the software itself** (not the organization or the repository) is a different and much bigger job: the name is in the program's package, its commands (`er3ds`), the zip's file name, the manual and the window, as well as in the site.

## What is in this folder

```
index.html  download.html  workflow.html  tutorials.html  citations.html  404.html
assets/     css/style.css  js/site.js  img/ (logo, icons, illustrations, figures)
data/       site.json  tutorials.json  (release.json only in the "local" way)
tools/      sync_chrome.py  build_citations.py  update_release.py  set_site_url.py  check_site.py  make_illustrations.py
_partials/  header.html  footer.html
downloads/  (only for the "local" way)      videos/  (your video files)
```

The figures on the Workflow page are real output of the program (their captions say for which data); the three drawings of the first steps are illustrations and are labelled as such. The logo files are the ones of the program.
