"""Build truthful, static profile/sharing metadata from reviewed public content."""
from __future__ import annotations
import html
import json
from pathlib import Path
import re
import struct
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

BRAND_ASSETS = (
    "assets/brand/kytt-macmanus-mark.svg", "assets/brand/kytt-macmanus-mark-reverse.svg",
    "assets/brand/kytt-macmanus-wordmark.svg", "assets/brand/kytt-macmanus-mark.png",
    "assets/brand/kytt-macmanus-mark-reverse.png", "assets/brand/favicon-96.png",
    "assets/brand/favicon.ico", "assets/brand/apple-touch-icon.png",
    "assets/brand/social-card.svg", "assets/brand/social-card.png",
)
METADATA_ASSETS = ("sitemap.xml", "content/site.json", "tools/site_metadata.py", *BRAND_ASSETS)

def png_dimensions(path):
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Expected a real PNG"
    return struct.unpack(">II", data[16:24])

def validate_config(config, site):
    expected = {"canonicalUrl", "title", "siteName", "description", "shareTitle", "shareDescription", "shareImage", "shareImageAlt", "personName", "personDescription", "topics", "language", "locale", "themeColor"}
    assert set(config) == expected, "Unreviewed metadata field"
    canonical = urlparse(config["canonicalUrl"])
    assert canonical.scheme == "https" and canonical.netloc == "kyttmacmanus.github.io" and canonical.path == "/career-timeline/"
    assert not canonical.query and not canonical.fragment and not canonical.username
    assert config["personName"] == "Kytt MacManus"
    assert config["shareImage"] == "assets/brand/social-card.png"
    assert all(isinstance(config[k], str) and config[k].strip() for k in expected - {"topics"})
    assert config["topics"] and all(isinstance(x, str) and x for x in config["topics"])
    assert re.fullmatch(r"#[0-9a-fA-F]{6}", config["themeColor"])
    for relative in BRAND_ASSETS:
        assert (site / relative).is_file(), "Missing brand export: " + relative
    assert png_dimensions(site / config["shareImage"]) == (1200, 630)
    assert png_dimensions(site / "assets/brand/favicon-96.png") == (96, 96)
    assert png_dimensions(site / "assets/brand/apple-touch-icon.png") == (180, 180)

def structured_data(data, config):
    base = config["canonicalUrl"]
    person = {"@type": "Person", "@id": base + "#person", "name": config["personName"],
              "url": base, "description": config["personDescription"], "knowsAbout": config["topics"]}
    profile = {"@type": "ProfilePage", "@id": base + "#profile", "url": base,
               "name": config["siteName"], "description": config["description"], "inLanguage": config["language"],
               "lastReviewed": data["updated"], "mainEntity": {"@id": person["@id"]},
               "mentions": {"@id": base + "#timeline"}}
    timeline = {"@type": "ItemList", "@id": base + "#timeline", "url": base + "#timeline",
                "name": "Career milestones, most recent first", "itemListOrder": "https://schema.org/ItemListOrderDescending",
                "numberOfItems": len(data["milestones"]), "itemListElement": [
                    {"@type": "ListItem", "position": i, "name": item["title"], "url": base + "#" + item["id"]}
                    for i, item in enumerate(data["milestones"], 1)]}
    return {"@context": "https://schema.org", "@graph": [profile, person, timeline]}

def render_metadata(data, config):
    e = lambda value: html.escape(str(value), quote=True)
    image_url = urljoin(config["canonicalUrl"], config["shareImage"])
    lines = ['  <!-- SITE_METADATA_START -->', '  <meta charset="utf-8">',
             '  <meta name="viewport" content="width=device-width, initial-scale=1">',
             f'  <title>{e(config["title"])}</title>',
             f'  <meta name="description" content="{e(config["description"])}">',
             f'  <meta name="author" content="{e(config["personName"])}">',
             f'  <meta name="theme-color" content="{e(config["themeColor"])}">',
             '  <meta name="robots" content="index,follow,max-image-preview:large">',
             f'  <link rel="canonical" href="{e(config["canonicalUrl"])}">',
             '  <link rel="icon" type="image/x-icon" sizes="16x16 32x32 48x48" href="assets/brand/favicon.ico">',
             '  <link rel="icon" type="image/png" sizes="96x96" href="assets/brand/favicon-96.png">',
             '  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">',
             '  <link rel="apple-touch-icon" sizes="180x180" href="assets/brand/apple-touch-icon.png">']
    og = {"og:type": "website", "og:title": config["shareTitle"], "og:description": config["shareDescription"],
          "og:url": config["canonicalUrl"], "og:site_name": config["siteName"], "og:locale": config["locale"],
          "og:image": image_url, "og:image:type": "image/png", "og:image:width": 1200, "og:image:height": 630,
          "og:image:alt": config["shareImageAlt"]}
    lines += [f'  <meta property="{e(key)}" content="{e(value)}">' for key, value in og.items()]
    compatibility = {"twitter:card": "summary_large_image", "twitter:title": config["shareTitle"],
                     "twitter:description": config["shareDescription"], "twitter:image": image_url,
                     "twitter:image:alt": config["shareImageAlt"]}
    lines += [f'  <meta name="{e(key)}" content="{e(value)}">' for key, value in compatibility.items()]
    payload = json.dumps(structured_data(data, config), ensure_ascii=False, indent=2).replace("</", "<\\/")
    lines += ['  <script type="application/ld+json">' + payload + '</script>', '  <!-- SITE_METADATA_END -->']
    return "\n".join(lines)

def apply_metadata(page, data, site):
    config = json.loads((site / "content/site.json").read_text(encoding="utf-8"))
    validate_config(config, site)
    metadata = render_metadata(data, config)
    if '<!-- SITE_METADATA_START -->' in page:
        page = re.sub(r'(?s)  <!-- SITE_METADATA_START -->.*?  <!-- SITE_METADATA_END -->', lambda _: metadata, page, count=1)
    else:
        start = page.index('<head>') + len('<head>')
        end = page.index('  <link rel="stylesheet"', start)
        page = page[:start] + "\n" + metadata + "\n" + page[end:]
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    sitemap = ET.Element("{" + namespace + "}urlset")
    url = ET.SubElement(sitemap, "{" + namespace + "}url")
    ET.SubElement(url, "{" + namespace + "}loc").text = config["canonicalUrl"]
    ET.SubElement(url, "{" + namespace + "}lastmod").text = data["updated"]
    (site / "sitemap.xml").write_bytes(ET.tostring(sitemap, encoding="utf-8", xml_declaration=True) + b"\n")
    return page
