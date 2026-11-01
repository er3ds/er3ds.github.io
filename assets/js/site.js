/* ER3DS website: small enhancements. The pages are complete without this file; it adds the menu button on small screens, the install tabs and copy buttons,
   the numbers of the current release (data/release.json), the links to GitHub (data/site.json) and the video cards (data/tutorials.json).
   No library, no cookie, nothing is loaded from another site (a YouTube video is only contacted after the visitor clicks its play button). */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  function getJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) { throw new Error(path + ": " + r.status); }
      return r.json();
    });
  }

  /* ---------------------------------------------------------------- menu button (small screens) */
  var toggle = $(".nav-toggle");
  var nav = $("#site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------------------------------------------------------------- footer year */
  $$("[data-year]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  /* ---------------------------------------------------------------- tabs (install: Windows / macOS / Linux) */
  $$(".tabs").forEach(function (box) {
    var tabs = $$('[role="tab"]', box);
    var panels = $$('[role="tabpanel"]', box);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function (p) { p.hidden = p.id !== tab.getAttribute("aria-controls"); });
      if (focus) { tab.focus(); }
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t, false); });
      t.addEventListener("keydown", function (e) {
        var j = null;
        if (e.key === "ArrowRight") { j = (i + 1) % tabs.length; }
        if (e.key === "ArrowLeft") { j = (i - 1 + tabs.length) % tabs.length; }
        if (e.key === "Home") { j = 0; }
        if (e.key === "End") { j = tabs.length - 1; }
        if (j !== null) { e.preventDefault(); select(tabs[j], true); }
      });
    });
    if (box.hasAttribute("data-os-tabs")) {                      /* open the tab of the visitor's system */
      var ua = (navigator.userAgent || "") + " " + (navigator.platform || "");
      var want = /Win/i.test(ua) ? "windows" : (/Mac|iPhone|iPad/i.test(ua) ? "macos" : (/Linux|X11|CrOS/i.test(ua) ? "linux" : ""));
      var pick = tabs.filter(function (t) { return t.getAttribute("data-os") === want; })[0];
      if (pick) { select(pick, false); }
    }
  });

  /* ---------------------------------------------------------------- copy buttons */
  $$(".code .copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var pre = $("pre", btn.parentNode);
      var text = pre ? pre.textContent.replace(/\s+$/, "") : "";
      function done(ok) {
        var old = btn.getAttribute("data-label") || btn.textContent;
        btn.setAttribute("data-label", old);
        btn.textContent = ok ? "Copied" : "Press Ctrl+C";
        setTimeout(function () { btn.textContent = old; }, 1800);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        var ok = false;
        try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
        document.body.removeChild(ta);
        done(ok);
      }
    });
  });

  /* ---------------------------------------------------------------- the current release
     Two ways to offer the zip (data/site.json: "download_mode"):
       "github-release": the zip is attached to a release of your GitHub repository; the page asks GitHub for the LATEST release (version, date, size, link), so publishing a new release updates the page.
       "local":          the zip is a file of this site (downloads/er3ds.zip) described by data/release.json (written by tools/update_release.py).
     The page shows nothing it does not know: a number that cannot be found is left out, never guessed. */
  function formatBytes(n) {
    if (typeof n !== "number" || !isFinite(n)) { return ""; }
    if (n >= 1048576) { return (n / 1048576).toFixed(1) + " MB"; }
    return Math.max(1, Math.round(n / 1024)) + " KB";
  }
  function formatDate(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) { return ""; }
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
  }
  function parseRepo(url) {
    var m = /^https:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?\/?$/.exec(url || "");
    return m ? { owner: m[1], name: m[2], base: "https://github.com/" + m[1] + "/" + m[2] } : null;
  }
  function showRelease(values, urls) {
    $$("[data-release]").forEach(function (el) {
      var v = values[el.getAttribute("data-release")];
      if (v) { el.textContent = (el.getAttribute("data-prefix") || "") + v; }
    });
    $$("[data-release-row]").forEach(function (row) { row.hidden = !values[row.getAttribute("data-release-row")]; });
    $$("[data-release-link]").forEach(function (a) {
      var url = urls[a.getAttribute("data-release-link")];
      if (url) { a.setAttribute("href", url); a.hidden = false; } else { a.hidden = true; }
    });
    $$("[data-release-missing]").forEach(function (el) { el.hidden = true; });
  }
  function notSetUp() {
    $$("[data-release-missing]").forEach(function (el) { el.hidden = false; });
    $$("[data-release-link]").forEach(function (a) {
      if (a.getAttribute("data-release-link") === "file") { a.setAttribute("href", "#"); a.setAttribute("aria-disabled", "true"); a.classList.add("disabled"); }
      else { a.hidden = true; }
    });
  }
  function fromLocal() {
    return getJSON("data/release.json").then(function (rel) {
      showRelease({ version: rel.version ? "v" + rel.version : "", date: formatDate(rel.date), size: formatBytes(rel.size_bytes), sha256: rel.sha256 || "",
                    file: rel.file || "", "manual-size": rel.manual ? formatBytes(rel.manual.size_bytes) : "" },
                  { file: rel.url, manual: rel.manual && rel.manual.url });
    }, notSetUp);
  }
  function fromGitHub(repo) {
    var zip = repo.base + "/releases/latest/download/er3ds.zip";
    var pdf = repo.base + "/releases/latest/download/ER3DS_manual.pdf";
    showRelease({}, { file: zip, manual: pdf });                                  /* usable at once; the numbers follow if GitHub answers */
    return fetch("https://api.github.com/repos/" + repo.owner + "/" + repo.name + "/releases/latest", { headers: { Accept: "application/vnd.github+json" } }).then(function (r) {
      if (r.status === 404) { showRelease({}, { file: repo.base + "/releases", manual: repo.base + "/releases" }); return null; }
      if (!r.ok) { return null; }
      return r.json();
    }).then(function (rel) {
      if (!rel || !rel.assets) { return; }
      var asset = rel.assets.filter(function (a) { return a.name === "er3ds.zip"; })[0] || rel.assets.filter(function (a) { return /\.zip$/i.test(a.name); })[0];
      var man = rel.assets.filter(function (a) { return a.name === "ER3DS_manual.pdf"; })[0];
      if (!asset) { showRelease({}, { file: rel.html_url || repo.base + "/releases", manual: man && man.browser_download_url }); return; }
      var digest = /^sha256:([0-9a-f]{64})$/.exec(asset.digest || "");
      showRelease({ version: (rel.tag_name || "").replace(/^[vV]/, "") ? "v" + (rel.tag_name || "").replace(/^[vV]/, "") : "", date: formatDate(rel.published_at), size: formatBytes(asset.size),
                    sha256: digest ? digest[1] : "", file: asset.name, "manual-size": man ? formatBytes(man.size) : "" },
                  { file: asset.browser_download_url, manual: man && man.browser_download_url });
    }).catch(function () { /* offline, or GitHub's limit for anonymous visitors: the links above still work */ });
  }
  if ($$("[data-release]").length || $$("[data-release-link]").length) {
    getJSON("data/site.json").then(function (s) { return s; }, function () { return {}; }).then(function (site) {
      var repo = parseRepo(site.github_repo_url);
      var mode = site.download_mode || (repo ? "github-release" : "local");
      if (mode === "github-release") { return repo ? fromGitHub(repo) : notSetUp(); }
      return fromLocal();
    });
  }

  /* ---------------------------------------------------------------- links to GitHub and the contact (data/site.json) */
  if ($$("[data-site]").length) {
    getJSON("data/site.json").then(function (site) {
      var repo = (site.github_repo_url || "").replace(/\/+$/, "");
      $$("[data-site]").forEach(function (el) {
        var kind = el.getAttribute("data-site");
        var url = "";
        if (kind === "github" && repo) { url = repo; }
        if (kind === "issues" && repo) { url = repo + "/issues"; }
        if (kind === "releases" && repo) { url = repo + "/releases"; }
        if (kind === "contact" && site.contact_email) { url = "mailto:" + site.contact_email; }
        if (url) { el.setAttribute("href", url); el.hidden = false; }
      });
      $$("[data-site-text]").forEach(function (el) {
        var v = site[el.getAttribute("data-site-text")];
        if (v) { el.textContent = v; el.hidden = false; }
      });
    }).catch(function () { /* optional */ });
  }

  /* ---------------------------------------------------------------- video tutorials (data/tutorials.json) */
  var list = $("#tutorial-list");
  if (list) {
    var PLAY = '<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#ffffff" fill-opacity=".16" stroke="#ffffff" stroke-width="2.5"/><path d="M26 20 L46 32 L26 44 Z" fill="#ffffff"/></svg>';
    var el = function (tag, cls, text) {
      var e = document.createElement(tag);
      if (cls) { e.className = cls; }
      if (text) { e.textContent = text; }
      return e;
    };
    var isId = function (s) { return /^[A-Za-z0-9_-]{6,20}$/.test(s || ""); };
    var isLocal = function (s) { return /^videos\/[A-Za-z0-9._\/-]+\.(mp4|webm)$/.test(s || ""); };

    getJSON("data/tutorials.json").then(function (data) {
      var items = (data && data.tutorials) || [];
      var empty = $("#tutorial-empty");
      if (!items.length) { if (empty) { empty.hidden = false; } return; }
      if (empty) { empty.hidden = true; }
      items.forEach(function (t) {
        var card = el("article", "card video-card");
        var frame = el("div", "video-frame");
        if (isLocal(t.video)) {
          var v = document.createElement("video");
          v.controls = true; v.preload = "metadata";
          if (t.poster && /^(assets|videos)\/[A-Za-z0-9._\/-]+$/.test(t.poster)) { v.poster = t.poster; }
          var src = document.createElement("source");
          src.src = t.video; src.type = /\.webm$/.test(t.video) ? "video/webm" : "video/mp4";
          v.appendChild(src);
          v.setAttribute("aria-label", t.title || "Tutorial video");
          frame.appendChild(v);
        } else if (isId(t.youtube)) {
          var b = el("button", "play");
          b.type = "button";
          b.setAttribute("aria-label", "Play the video: " + (t.title || "tutorial"));
          b.innerHTML = PLAY + '<span>Play video</span>';
          b.addEventListener("click", function () {
            var f = document.createElement("iframe");
            f.src = "https://www.youtube-nocookie.com/embed/" + t.youtube + "?autoplay=1&rel=0";
            f.title = t.title || "Tutorial video";
            f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
            f.allowFullscreen = true;
            f.loading = "lazy";
            frame.replaceChild(f, b);
          });
          frame.appendChild(b);
        } else {
          frame.appendChild(el("span", "", "Video not available"));
        }
        card.appendChild(frame);
        var body = el("div", "video-body");
        body.appendChild(el("h3", "", t.title || "Untitled tutorial"));
        var meta = [t.level, t.duration].filter(Boolean).join(" \u00b7 ");
        if (meta) { body.appendChild(el("p", "muted small", meta)); }
        if (t.description) { body.appendChild(el("p", "", t.description)); }
        card.appendChild(body);
        list.appendChild(card);
      });
    }).catch(function () {
      var empty = $("#tutorial-empty");
      if (empty) { empty.hidden = false; }
    });
  }
})();
