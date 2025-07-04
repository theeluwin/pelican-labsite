from pathlib import Path
from datetime import datetime
from operator import itemgetter
from collections import OrderedDict

from pelican import signals


def parse_list(values):
    if isinstance(values, str):
        values = [str(value).strip() for value in values.split(',')]
    elif isinstance(values, list):
        values = [str(value).strip() for value in values]
    return values


def parse_metadata(fpath):
    metadata = {}
    content = fpath.read_text(encoding='utf-8')
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            break
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'date':
                value = datetime.strptime(value, '%Y-%m-%d')
            metadata[key] = value
    return metadata


class DB:

    DATA_ROOT = Path('content/data')

    def __init__(self):
        self.load_headlines()
        self.load_lectures()
        self.load_members()
        self.load_projects()
        self.load_publications()  # always last

    def load_headlines(self):
        headlines = []
        for fpath in (self.DATA_ROOT / 'headlines').glob('*.md'):
            headline = parse_metadata(fpath)
            headlines.append(headline)
        headlines = sorted(headlines, key=itemgetter('slug'), reverse=True)
        self.headlines = headlines

    def load_lectures(self):
        lectures = []
        yearset = set()
        cache = {}
        for fpath in (self.DATA_ROOT / 'lectures').glob('*.md'):
            lecture = parse_metadata(fpath)
            year = int(lecture['year'])
            yearset.add(year)
            lecture['year'] = year
            lecture['assitants'] = parse_list(lecture['assitants'])
            semester = lecture['semester']
            key = (year, semester)
            if key not in cache:
                cache[key] = []
            cache[key].append(lecture)
            lectures.append(lecture)
        data = OrderedDict()
        years = sorted(list(yearset), reverse=True)
        for year in years:
            data[year] = OrderedDict()
            for semester in ['Fall', 'Spring']:
                if (year, semester) in cache:
                    rows = cache[(year, semester)]
                    rows = sorted(rows, key=itemgetter('date'), reverse=True)
                    data[year][semester] = rows
            if not data[year]:
                del data[year]
        self.lectures = lectures
        self.verbose_lecture_data = data

    def load_members(self):
        members = []
        title2member = {}
        cache_current = {}
        cache_alumni = {}
        for fpath in (self.DATA_ROOT / 'members').glob('*.md'):
            member = parse_metadata(fpath)
            member['joined_date'] = datetime.strptime(member['joined_date'], '%Y-%m-%d')
            key = member['position']
            if member['membership'] == 'current':
                if key not in cache_current:
                    cache_current[key] = []
                cache_current[key].append(member)
            elif member['membership'] == 'alumni':
                member['graduated_date'] = datetime.strptime(member['graduated_date'], '%Y-%m-%d')
                if key not in cache_alumni:
                    cache_alumni[key] = []
                cache_alumni[key].append(member)
            members.append(member)
            title2member[member['title']] = member
        data_current = OrderedDict()
        for position in ['Professor', 'PhD Candidate', 'PhD Student', 'Master Student', 'Intern']:
            if position in cache_current:
                rows = cache_current[position]
                rows = sorted(rows, key=itemgetter('joined_date'), reverse=True)
                data_current[position] = rows
        data_alumni = OrderedDict()
        for position in ['PhD', 'Master']:
            if position in cache_alumni:
                rows = cache_alumni[position]
                rows = sorted(rows, key=itemgetter('graduated_date'), reverse=True)
                data_alumni[position] = rows
        self.members = members
        self.title2member = title2member
        self.verbose_current_member_data = data_current
        self.verbose_alumni_member_data = data_alumni

    def load_projects(self):
        projects = []
        slug2project = {}
        for fpath in (self.DATA_ROOT / 'projects').glob('*.md'):
            project = parse_metadata(fpath)
            slug = project['slug']
            slug2project[slug] = project
            projects.append(project)
        projects = sorted(projects, key=itemgetter('date'), reverse=True)
        self.projects = projects
        self.slug2project = slug2project

    def load_publications(self):
        publications = []
        yearset = set()
        cache = {}
        for fpath in (self.DATA_ROOT / 'publications').glob('*.md'):
            publication = parse_metadata(fpath)
            year = int(publication['year'])
            yearset.add(year)
            publication['year'] = year
            authors = parse_list(publication['authors'])
            publication['authors'] = authors
            for title in authors:
                if title not in self.title2member:
                    continue
                member = self.title2member[title]
                if 'publications' not in member:
                    member['publications'] = []
                member['publications'].append(publication)
            publication['projects'] = parse_list(publication['projects'])
            for slug in publication['projects']:
                if slug not in self.slug2project:
                    continue
                project = self.slug2project[slug]
                if 'publications' not in project:
                    project['publications'] = []
                project['publications'].append(publication)
            key = (year, publication['venue_scope'], publication['venue_type'])
            if key not in cache:
                cache[key] = []
            cache[key].append(publication)
            publications.append(publication)
        publications = sorted(publications, key=itemgetter('date'), reverse=True)
        for title in self.title2member:
            member = self.title2member[title]
            if 'publications' not in member:
                member['publications'] = []
            member['publications'] = sorted(member['publications'], key=itemgetter('date'), reverse=True)
        for slug in self.slug2project:
            project = self.slug2project[slug]
            if 'publications' not in project:
                project['publications'] = []
            project['publications'] = sorted(project['publications'], key=itemgetter('date'), reverse=True)
        data = OrderedDict()
        years = sorted(list(yearset), reverse=True)
        for year in years:
            data[year] = OrderedDict()
            for venue_scope in ['Global', 'Domestic']:
                data[year][venue_scope] = OrderedDict()
                for venue_type in ['Conference', 'Journal']:
                    if (year, venue_scope, venue_type) in cache:
                        rows = cache[(year, venue_scope, venue_type)]
                        rows = sorted(rows, key=itemgetter('date'), reverse=True)
                        data[year][venue_scope][venue_type] = rows
                if not data[year][venue_scope]:
                    del data[year][venue_scope]
            if not data[year]:
                del data[year]
        self.publications = publications
        self.verbose_publication_data = data


db = DB()


def get_publications_by_member_title(title):
    title = str(title).strip()
    if title not in db.title2member:
        return []
    member = db.title2member[title]
    return member['publications']


def get_publications_by_project_slug(slug):
    slug = str(slug).strip()
    if slug not in db.slug2project:
        return []
    project = db.slug2project[slug]
    return project['publications']


def filter_linkify_members(titles):
    anchors = []
    for title in titles:
        title = str(title).strip()
        if title in db.title2member:
            member = db.title2member[title]
            anchor = f"<a href='/member/{member['slug']}.html'>{title}</a>"
        else:
            anchor = title
        anchors.append(anchor)
    return ', '.join(anchors)


def add_context(generator, metadata):
    generator.context['RECENT_DATA_LIMIT'] = generator.settings.get('RECENT_DATA_LIMIT', 5)
    generator.context['all_headlines'] = db.headlines
    generator.context['verbose_lecture_data'] = db.verbose_lecture_data
    generator.context['verbose_current_member_data'] = db.verbose_current_member_data
    generator.context['verbose_alumni_member_data'] = db.verbose_alumni_member_data
    generator.context['all_projects'] = db.projects
    generator.context['all_publications'] = db.publications
    generator.context['verbose_publication_data'] = db.verbose_publication_data
    generator.context['get_publications_by_member_title'] = get_publications_by_member_title
    generator.context['get_publications_by_project_slug'] = get_publications_by_project_slug


def add_filters(pelican):
    if 'JINJA_FILTERS' not in pelican.settings:
        pelican.settings['JINJA_FILTERS'] = {}
    pelican.settings['JINJA_FILTERS']['linkify_members'] = filter_linkify_members


def register():
    signals.article_generator_context.connect(add_context)
    signals.page_generator_context.connect(add_context)
    signals.initialized.connect(add_filters)
