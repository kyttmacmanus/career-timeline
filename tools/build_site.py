"""Validate the public allowlist and build a GitHub Pages static artifact.

Only explicitly listed site files enter the artifact. The surrounding archive,
review records, scripts, and private databases are never copied.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content/milestones.json"
ASSETS = ("style.css", "app.js", "milestones.js")
PRIVATE_HOSTS = {"mail.google.com", "docs.google.com", "drive.google.com", "localhost", "127.0.0.1"}
IMAGE_RIGHTS = {"institutional_archive_approved", "author_owned", "cc_by", "cc_by_sa", "public_domain", "permission_granted", "license_permits_reuse"}
IMAGE_PATH = re.compile(r"assets/media/[a-z0-9][a-z0-9._-]*\.(?:webp|jpg|jpeg|png)", re.I)


def public_url(value):
    u = urlparse(value)
    return u.scheme == "https" and u.hostname and not u.username and not u.password and u.hostname not in PRIVATE_HOSTS


def validate_media(media):
    assert isinstance(media, dict), "Media entry must be an object"
    kind = media.get("kind")
    if kind == "image":
        assert IMAGE_PATH.fullmatch(media.get("src", "")), "Image must use an allowlisted assets/media filename"
        path = ROOT / media["src"]
        assert path.resolve().parent == (ROOT / "assets/media").resolve(), "Image escapes media directory"
        assert path.is_file(), "Missing image derivative: " + media["src"]
        assert path.stat().st_size <= 5 * 1024 * 1024, "Use an optimized image derivative"
        assert media.get("rights") in IMAGE_RIGHTS, "Image reuse decision is not approved"
        if media.get("rights") in {"cc_by", "cc_by_sa"}:
            assert media.get("licenseUrl"), "Creative Commons attribution needs its license link"
        if media.get("licenseUrl"):
            assert public_url(media["licenseUrl"]), "Image license must use a public HTTPS destination"
        if "rightsLabel" in media:
            assert isinstance(media["rightsLabel"], str)
        for key in ("alt", "caption", "credit", "sourceUrl", "sourceTitle"):
            assert isinstance(media.get(key), str) and media[key].strip(), "Image missing " + key
        assert public_url(media["sourceUrl"]), "Image source must be a public HTTPS destination"
        assert all(type(media.get(key)) is int and 0 < media[key] <= 20000 for key in ("width", "height")), "Image dimensions missing or invalid"
    else:
        assert kind in {"video", "interactive", "slides", "article"}, "Unsupported media kind"
        assert isinstance(media.get("title"), str) and media["title"].strip(), "Media link needs a title"
        assert public_url(media.get("url", "")), "Media link must be public HTTPS"
        assert "caption" not in media or isinstance(media["caption"], str)


def sort_key(item):
    parts = item["date"].split("-")
    season_order = {"spring": 3, "summer": 6, "fall": 9, "winter": 12}
    # Seasonal ordering does not turn a term into an invented event date.
    month = int(parts[1]) if len(parts) > 1 else season_order.get(item.get("season"), 0)
    day = int(parts[2]) if len(parts) > 2 else 0
    return int(parts[0]), month, day, item["title"]


def validate(data):
    reviewed = date.fromisoformat(data["updated"])
    assert data["milestones"], "Timeline cannot be empty"
    ids = set()
    for item in data["milestones"]:
        for field in ("id", "date", "datePrecision", "dateLabel", "title", "summary", "role", "themes", "type", "status", "featured", "sources"):
            assert field in item, f"{item.get('id')}: missing {field}"
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"])
        assert item["id"] not in ids, "Duplicate milestone ID"
        ids.add(item["id"])
        assert re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", item["date"])
        parsed = date.fromisoformat((item["date"] + "-01-01")[:10])
        assert parsed <= reviewed, "Achievement is after the recorded review date"
        assert item["datePrecision"] in {"year", "month", "day", "range"}
        assert item["status"] == "completed", "Current allowlist contains completed milestones only"
        assert isinstance(item["featured"], bool) and item["themes"] and item["sources"]
        assert isinstance(item.get("media", []), list), "Media must be an array"
        for media in item.get("media", []):
            validate_media(media)
        for source in item["sources"]:
            u = urlparse(source["url"])
            assert u.scheme == "https" and u.hostname and not u.username and not u.password
            assert u.hostname not in PRIVATE_HOSTS, "Private source leaked into public data"
            assert source["title"].strip()
        text = json.dumps(item, ensure_ascii=False)
        assert not re.search(r"\b[A-Z]:[\\/]|THUNDERBIRD|GMAIL:|source_message_id|salary|passport|Rascal", text, re.I), "Private archive field in public data"
        assert len(item["summary"]) <= 600
    return {"milestones": len(ids), "featured": sum(x["featured"] for x in data["milestones"]), "first_year": min(x["date"][:4] for x in data["milestones"]), "last_year": max(x["date"][:4] for x in data["milestones"]), "media_milestones": sum(bool(x.get("media")) for x in data["milestones"]), "media_images": sum(m.get("kind") == "image" for x in data["milestones"] for m in x.get("media", []))}


def media_markup(item):
    e = html.escape
    parts = []
    for index, media in enumerate(item.get("media", [])):
        if media["kind"] == "image":
            rights = f' · <a href="{e(media["licenseUrl"], quote=True)}" rel="noopener">{e(media.get("rightsLabel") or "Reuse license")}</a>' if media.get("licenseUrl") else ' · ' + e(media["rightsLabel"]) if media.get("rightsLabel") else ''
            parts.append(f'''<figure class="milestone-image"><a class="media-preview" href="{e(media['src'], quote=True)}" data-image-open data-milestone-id="{e(item['id'])}" data-media-index="{index}" aria-label="Enlarge image: {e(media['alt'], quote=True)}"><img src="{e(media['src'], quote=True)}" alt="{e(media['alt'], quote=True)}" width="{media['width']}" height="{media['height']}" loading="lazy" decoding="async"><span class="media-enlarge" aria-hidden="true">Enlarge ↗</span></a><figcaption><span class="media-caption">{e(media['caption'])}</span><span class="media-credit">{e(media['credit'])}{rights}</span><a class="media-source" href="{e(media['sourceUrl'], quote=True)}" rel="noopener">{e(media['sourceTitle'])} ↗</a></figcaption></figure>''')
        else:
            label = {"video": "Watch video", "interactive": "Explore interactive", "slides": "View slides", "article": "Read the story"}[media["kind"]]
            caption = f'<p>{e(media["caption"])}</p>' if media.get("caption") else ""
            parts.append(f'''<div class="milestone-media-link"><span class="media-kind">{label}</span><a href="{e(media['url'], quote=True)}" rel="noopener">{e(media['title'])} <span aria-hidden="true">↗</span></a>{caption}</div>''')
    return '<div class="milestone-media">' + "".join(parts) + '</div>' if parts else ""


def base_card(item):
    e = html.escape
    accents = {"Population & data": "#006575", "Climate & coasts": "#6853a2", "Teaching": "#087fab", "Open science": "#775b2b", "Field methods": "#28734b", "Leadership": "#ac4e34"}
    accent = next((accents[t] for t in item["themes"] if t in accents), "#006575")
    links = "".join(f'<li><a href="{e(s["url"], quote=True)}" rel="noopener">{e(s["title"])} <span aria-hidden="true">↗</span></a></li>' for s in item["sources"])
    tags = "".join(f'<span class="theme-label">{e(t)}</span>' for t in item["themes"])
    context = f'<p class="milestone-context">{e(item["detail"])}</p>' if item.get("detail") else ""
    return f'''<li class="timeline-item" id="{e(item['id'])}" style="--card-accent:{accent}"><article class="milestone" aria-labelledby="title-{e(item['id'])}"><div class="milestone-date-line"><time class="milestone-date" datetime="{e(item['date'])}">{e(item['dateLabel'])}</time><span class="milestone-kind">{e(item['type'])}</span></div><h3 id="title-{e(item['id'])}"><a href="#{e(item['id'])}">{e(item['title'])}</a></h3><p class="milestone-summary">{e(item['summary'])}</p><div class="milestone-themes">{tags}</div><details><summary>Contribution &amp; sources<span class="sr-only">: {e(item['title'])}</span></summary><p class="milestone-role"><strong>Kytt’s contribution</strong>{e(item['role'])}</p>{context}<p class="milestone-source-label">Explore this work</p><ul class="milestone-sources">{links}</ul><a class="permalink" href="#{e(item['id'])}">Link to this milestone <span aria-hidden="true">↗</span></a></details></article></li>'''


def static_card(item):
    return base_card(item).replace("</h3>", "</h3>" + media_markup(item), 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="New or existing output folder contained inside this site")
    args = parser.parse_args()
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    summary = validate(data)
    data["milestones"].sort(key=sort_key)
    # JSON is data, not executable text. Escape closing script-like sequences.
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    (ROOT / "assets/milestones.js").write_text("window.CAREER_DATA = " + payload + ";\n", encoding="utf-8")
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "<!-- TIMELINE_STATIC_START -->" in page and "<!-- TIMELINE_STATIC_END -->" in page
    cards = "\n".join(static_card(x) for x in data["milestones"])
    replacement = "<!-- TIMELINE_STATIC_START -->\n" + cards + "\n<!-- TIMELINE_STATIC_END -->"
    page = re.sub(r"(?s)<!-- TIMELINE_STATIC_START -->.*?<!-- TIMELINE_STATIC_END -->", lambda _: replacement, page)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    dest = ROOT if not args.output else (ROOT / args.output).resolve()
    assert dest == ROOT or (ROOT in dest.parents and dest.name not in {"content", "tools", "assets", ".github"}), "Output must be inside this site and outside source folders"
    if dest != ROOT:
        dest.mkdir(parents=True, exist_ok=True)
        for name in ("index.html", ".nojekyll"):
            shutil.copy2(ROOT / name, dest / name)
        (dest / "assets").mkdir(exist_ok=True)
        for name in ASSETS:
            shutil.copy2(ROOT / "assets" / name, dest / "assets" / name)
        # Copy only derivatives referenced by validated public records.
        # Never recursively copy private recovery or asset directories.
        media_assets = {m["src"] for item in data["milestones"] for m in item.get("media", []) if m["kind"] == "image"}
        for relative in sorted(media_assets):
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        (dest / "content").mkdir(exist_ok=True)
        shutil.copy2(CONTENT, dest / "content/milestones.json")
    print(json.dumps({"validated": True, "output": str(dest), **summary}))


if __name__ == "__main__":
    main()
