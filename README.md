# Kytt MacManus · career timeline

A static GitHub Pages website showing selected, sourced career milestones. The visual language follows Drones Helping People: slate and cyan, a light research-portfolio layout, an alternating timeline, and expandable contributions and source links.

The reviewed content currently spans 2008–2026. `content/milestones.json` is the editable source. The website includes only an explicit public allowlist. The complete archive review and unresolved evidence queue stay outside this folder.

## Preview

Python 3.10+ is sufficient. No npm installation or server backend is required.

```powershell
python tools/build_site.py
python -m http.server 8768 --bind 127.0.0.1
```

Open `http://127.0.0.1:8768/`. Opening `index.html` directly also works. Search, year/theme filters, selected/all views, chronological sorting, source panels, and milestone permalinks run in the browser. The complete included timeline is readable when JavaScript is disabled.

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
