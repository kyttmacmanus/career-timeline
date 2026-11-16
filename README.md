# Kytt MacManus · career timeline

A static GitHub Pages website showing selected, sourced career milestones. The visual language follows Drones Helping People: slate and cyan, a light research-portfolio layout, an alternating timeline, and expandable contributions and source links.

The reviewed content currently spans 2007–2026. `content/milestones.json` is the editable source. The website includes only an explicit public allowlist. The complete archive review and unresolved evidence queue stay outside this folder.

## Preview

Python 3.10+ is sufficient. No npm installation or server backend is required.

```powershell
python tools/build_site.py
python -m http.server 8768 --bind 127.0.0.1
```

Open `http://127.0.0.1:8768/`. Opening `index.html` directly also works. The timeline starts with the most recent achievements, including when JavaScript is disabled. Search, year/theme filters, highlights/all/image views, an optional oldest-first order, source panels, and milestone permalinks run in the browser.

## Edit a milestone

Edit `content/milestones.json`, then rerun the build. Each entry needs a stable ID, date with explicit precision, display date, title, summary, contribution, theme labels, event type, completed status, selection flag, and one or more public HTTPS sources. Do not use an article date as an exact delivery date or a dataset's observation year as its release year.

Public wording distinguishes individual contribution from team output. Proposals, planned meetings, expected outcomes, and unverified authorship do not enter the completed-achievement list. A source can be an official institutional page, publication, credited dataset/software record, or an identified project portfolio.

The build checks dates, IDs, sources and restricted fields, regenerates browser data and the no-JavaScript timeline, and can prepare the deployment artifact:

```powershell
python tools/build_site.py --output _site
```

## GitHub Pages

Create a dedicated repository from **this directory only**, for example `career-timeline`. Never publish the surrounding `career_archive_review` workspace.

Push this site's contents to the repository's `main` branch. In Settings → Pages, choose **GitHub Actions** as the source. The included workflow validates and builds the site, then deploys only the allowlisted `_site` artifact. Relative asset links work on project Pages URLs and custom domains.

Workflow references: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) and [the official Python setup action](https://github.com/actions/setup-python).

Review the website at [kyttmacmanus.github.io/career-timeline](https://kyttmacmanus.github.io/career-timeline/). The source repository is [kyttmacmanus/career-timeline](https://github.com/kyttmacmanus/career-timeline). GitHub Actions publishes updates pushed to `main`.

## Provenance and scope

Review date: November 15, 2026. The local email index ends October 24, 2025. A separate private review records whole-index screening, every curated event's selection/hold decision, public corroboration, and targeted connected-source checks. Screening is retrieval, not semantic validation of every message. This public selection is not a claim that every achievement in the archive has been independently verified.

Raw email, private document URLs, personnel appraisals, internal source IDs, contact details and private evidence exports are excluded. No analytics, tracking, external scripts or third-party fonts are loaded.

## Photos and multimedia

Each milestone includes original project multimedia: photographs, published figures and maps, software views, presentations or recordings, with dates, credits and source links. The **With images** view collects milestones with local images; **All milestones** includes original-publisher recordings, galleries and other resources as well. Click an image to enlarge it; the image links also work without JavaScript. Recording, slide, interactive-map and original-image links open the corresponding public materials without automatically loading an external player. Some photographs and historical tool views open at the original publisher; later project images are dated explicitly.

The image files under `assets/media/` preserve original photographs, figures and explicitly identified output panels, with incidental embedded metadata removed. Creative Commons figures retain author and license links; institutional photographs retain project credits. Recovery from a mailbox is provenance, not a general reuse license. Unattributed or contextually private media remain outside this repository.

To add media, extend an entry's `media` array with an approved local image or a public video/interactive/slides/gallery/visual/document/article link. The build validates the media metadata and copies only image paths explicitly referenced by the public records. Keep original messages, attachment originals and private recovery records outside the site.

The sedacR worked-example documentation retains its [complete MIT license notice](assets/licenses/sedacr-MIT.txt).

The design uses original project imagery, larger reading text, summaries before media and grouped image galleries. Previous `?view=media` links continue to open all milestones.

## Identity and sharing

The original KM mark appears in the header, footer and browser icon. Reusable vector and transparent PNG versions, a wordmark and a 1200 × 630 sharing card are in `assets/brand/`. These are personal identity graphics; they do not represent a university or project endorsement.

Edit `content/site.json` for the public title, description, canonical URL, topics and sharing card, then rebuild. The build writes the metadata into the initial HTML, including image dimensions and descriptions, and generates `sitemap.xml`. It also creates a ProfilePage with a Person and a list of the actual milestones. Filters and milestone fragments share the main page's canonical URL.

Update `canonicalUrl` when moving the site to another domain. Project-level icons work in browsers and on Apple devices; Google's search favicon and site-name rules apply at the hostname level. This project does not control the root of `kyttmacmanus.github.io`. Sharing previews and search updates depend on each service's crawl and cache.
