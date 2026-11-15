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
        for source in item["sources"]:
            u = urlparse(source["url"])
            assert u.scheme == "https" and u.hostname and not u.username and not u.password
            assert u.hostname not in PRIVATE_HOSTS, "Private source leaked into public data"
            assert source["title"].strip()
        text = json.dumps(item, ensure_ascii=False)
        assert not re.search(r"\b[A-Z]:[\\/]|THUNDERBIRD|GMAIL:|source_message_id|salary|passport|Rascal", text, re.I), "Private archive field in public data"
        assert len(item["summary"]) <= 600
    return {"milestones": len(ids), "featured": sum(x["featured"] for x in data["milestones"]), "first_year": min(x["date"][:4] for x in data["milestones"]), "last_year": max(x["date"][:4] for x in data["milestones"])}


def static_card(item):
    e = html.escape
    accents = {"Population & data": "#006575", "Climate & coasts": "#6853a2", "Teaching": "#087fab", "Open science": "#775b2b", "Field methods": "#28734b", "Leadership": "#ac4e34"}
    accent = next((accents[t] for t in item["themes"] if t in accents), "#006575")
    links = "".join(f'<li><a href="{e(s["url"], quote=True)}" rel="noopener">{e(s["title"])} <span aria-hidden="true">↗</span></a></li>' for s in item["sources"])
    tags = "".join(f'<span class="theme-label">{e(t)}</span>' for t in item["themes"])
    context = f'<p class="milestone-context">{e(item["detail"])}</p>' if item.get("detail") else ""
    return f'''<li class="timeline-item" id="{e(item['id'])}" style="--card-accent:{accent}"><article class="milestone" aria-labelledby="title-{e(item['id'])}"><div class="milestone-date-line"><time class="milestone-date" datetime="{e(item['date'])}">{e(item['dateLabel'])}</time><span class="milestone-kind">{e(item['type'])}</span></div><h3 id="title-{e(item['id'])}"><a href="#{e(item['id'])}">{e(item['title'])}</a></h3><p class="milestone-summary">{e(item['summary'])}</p><div class="milestone-themes">{tags}</div><details><summary>Contribution &amp; sources<span class="sr-only">: {e(item['title'])}</span></summary><p class="milestone-role"><strong>Kytt’s contribution</strong>{e(item['role'])}</p>{context}<p class="milestone-source-label">Explore the sources</p><ul class="milestone-sources">{links}</ul><a class="permalink" href="#{e(item['id'])}">Link to this milestone <span aria-hidden="true">↗</span></a></details></article></li>'''


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
    page = re.sub(r"(?s)<!-- TIMELINE_STATIC_START -->.*?<!-- TIMELINE_STATIC_END -->", "<!-- TIMELINE_STATIC_START -->\n" + cards + "\n<!-- TIMELINE_STATIC_END -->", page)
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
        (dest / "content").mkdir(exist_ok=True)
        shutil.copy2(CONTENT, dest / "content/milestones.json")
    print(json.dumps({"validated": True, "output": str(dest), **summary}))


if __name__ == "__main__":
    main()
