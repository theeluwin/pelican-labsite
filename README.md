# Pelican Labsite

[![Build and Deploy Site](https://github.com/theeluwin/pelican-labsite/actions/workflows/pelican-labsite.yml/badge.svg)](https://github.com/theeluwin/pelican-labsite/actions/workflows/pelican-labsite.yml)

An academic lab website builder based on [Pelican](https://getpelican.com/).

It manages and updates the site by treating the `*.md` files in `/src/content/data/` (that is, the articles) as a kind of structured data.

Key features:

* Home (index)
    * recent headlines
    * cecent publications
* About
* Members
    * list of current or alumni members
    * **relevant publications for each member**
    * **relevant lectures for each member**
* Projects
    * **relevant publications for each project**
* Publications
    * per year, type
    * **automatic link of members for each author**

Inspired by [IDS Lab.](https://ids.snu.ac.kr) and [theeluwin.github.io](https://theeluwin.github.io), which are also my works.

## Run

### Development

Uses `/Dockerfile.dev` with `/src` volume bound.

But since most of the code runs through the engine (below), hot-reload may not work properly.

To run the development environment,

```bash
docker build -f ./Dockerfile.dev -t pelican-labsite-dev .
docker run \
    -it \
    --rm \
    --init \
    --publish 8000:8000 \
    --volume ./src:/src \
    --name pelican-labsite-dev-container \
    pelican-labsite-dev
```

or simply,

```bash
./run_dev.sh
```

then, open your browser and go to `http://localhost:8000`.

### Production

In the production, the site is built in a python environment, and the resulting output (`/dist` inside the docker image) is served by nginx. Refer to `Dockerfile.prod` for details.

To run the production environment,

```bash
docker build -f ./Dockerfile.prod -t pelican-labsite .
docker stop pelican-labsite-container 2>/dev/null || true
docker rm pelican-labsite-container 2>/dev/null || true
docker run \
    -d \
    --init \
    --publish 80:80 \
    --volume ./shared:/shared \
    --name pelican-labsite-container \
    pelican-labsite
```

or simply,

```bash
./run_prod.sh
```

then, open your browser and go to `http://localhost`.

You can see the nginx logs in `/shared/logfiles/`.

## Settings

See `/src/pelicanconf.py` for configuration details.

Most settings don't require modification, but the values at the top of the file will likely need to be customized.

```python
AUTHOR = 'Your Name'
SITENAME = "Your Lab"
SITEURL = 'http://yourlab.university.edu'
THEME = 'theme-bootstrap/'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
RECENT_DATA_LIMIT = 5
```

For the custom domain, modify the file `/src/content/extra/CNAME` with content that specifies your domain:

```
yourlab.university.edu
```

## Theme

The actual appearance of the site is controlled by the theme.

Currently, two themes are provided:

* `theme-vanilla`: located in `/src/theme-vanilla`, a theme that uses plain HTML only.
* `theme-bootstrap`: located in `/src/theme-bootstrap/`, a sample theme styled with [Bootstrap](https://getbootstrap.com/).

## Engine

The code `/src/plugins/labsite/engine.py` reads and parses files from `/src/content/`, which is used for the template rendering.

It provides template tags and filters that support the key features described above.

## Page

Files under `/src/content/pages/` are used to manage pages.

Cover image inserted in a jumbotron style from `theme-bootstrap` should be specified using the `cover` field and stored in `/src/content/images/covers/`.

```markdown
title: About
slug: about
template: pages/about
cover: about.jpg

About content.
```

## Content

### Recommended Rules

Make sure that the filename of each `*.md` file in `/src/content/data/` matches its `slug` metadata field.

The metadata fields for all articles should begin with the following (see [docs](https://docs.getpelican.com/en/latest/content.html) for more detail):

```markdown
template: articles/lecture  # `.html` extension is not required
category: lecture  # match the name of the directory
status: published  # fixed value
date: 2026-03-01  # will be used appropriately
title: Introduction to Databases  # will be used appropriately
slug: 2026-spring-introduction-to-databases  # match the name of the file
```

Then, the custom field follows:

```markdown
template: articles/lecture
category: lecture
status: published
date: 2026-03-01
title: Introduction to Databases
slug: 2026-spring-introduction-to-databases
cover: lecture.jpg  # custom field
year: 2026  # custom field
semester: Spring  # custom field
assitants: Master Student2, PhD Student2  # custom field

Lecture Content 3.  # start with one linebreak, use markdown syntax from here
```

### Headline

* Sorted by `-slug`.

### Member

* For `'current'` members, sorted by `position` (`'Professor'`, `'PhD Candidate'`, `'PhD Student'`, `'Master Student'`, `'Intern'`), `joined_date`.
* For `'alumni'` members, sorted by `position` (`'PhD'`, `'Master'`), `graduated_date`.
* In the detail view, publications with `authors` matching `title` of a member will be displayed (multiple matches allowed, comma-separated).
* In the detail view, lectures with `assitants` matching `title` of a member will be displayed (multiple matches allowed, comma-separated).
* For images, save it to `/src/content/images/members/`.

### Project

* Sorted by `-date`.
* In the detail view, publications with `projects` matching `slug` of a project will be displayed (multiple matches allowed, comma-separated).
* For images, save it to `/src/content/images/projects/`.

### Publication

* Sort by `-year`, `venue_type` (`'Preprint'`, `'Conference'`, `'Journal'`), `-date`.
* It also automatically generates links for members in `authors` field by matching their `title` (comma-separated).
* For images, save it to `/src/content/images/publications/`.

### Lecture

* Sort by `-year`, `semester` (`'Fall'`, `'Summer'`, `'Spring'`, `'Winter'`), `-date`.
* You can change the semester order from `/src/plugins/labsite/engine.py`.
* It also automatically generates links for members in `assistants` field by matching their `title` (comma-separated).

## Publishing to GitHub Pages

Use custom workflow. In your repo, go to Settings &rightarrow; Pages and choose GitHub Actions for the Source setting.

See `/.github/workflows/pelican-labsite.yml` for more details.
