from pathlib import Path
from datetime import datetime
from operator import itemgetter
from collections import OrderedDict

from pelican import signals


def parse_list(values):

    # comma-separated string
    if isinstance(values, str):
        values = [str(value).strip() for value in values.split(',')]

    # plain list
    elif isinstance(values, list):
        values = [str(value).strip() for value in values]

    return values


def parse_metadata(fpath):

    # prepare
    metadata = {}

    # read
    content = fpath.read_text(encoding='utf-8')

    # parse
    for line in content.split('\n'):
        line = line.strip()

        # stop at empty line
        if not line:
            break

        # parse key-value pair
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            # parse date
            if key == 'date':
                value = datetime.strptime(value, '%Y-%m-%d')

            # memorize
            metadata[key] = value

    return metadata


class Singleton:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


class DB(Singleton):

    DATA_ROOT = Path('content/data')

    def __init__(self):
        self.load_headlines()
        self.load_members()
        self.load_projects()
        self.load_publications()  # order matters
        self.load_lectures()  # order matters

    def load_headlines(self):

        # prepare
        headlines = []

        # load
        for fpath in (self.DATA_ROOT / 'headlines').glob('*.md'):
            headline = parse_metadata(fpath)
            headlines.append(headline)

        # sort
        headlines = sorted(headlines, key=itemgetter('slug'), reverse=True)

        # memorize
        self.headlines = headlines

    def load_members(self):

        # prepare
        members = []
        cache_current = {}
        cache_alumni = {}

        # for `filter_linkify_members` and `get_publications_by_member_title`
        title2member = {}

        # load
        for fpath in (self.DATA_ROOT / 'members').glob('*.md'):
            member = parse_metadata(fpath)

            # parse date
            try:
                member['joined_date'] = datetime.strptime(member['joined_date'], '%Y-%m-%d')
            except (KeyError, ValueError):
                member['joined_date'] = None
            try:
                member['graduated_date'] = datetime.strptime(member['graduated_date'], '%Y-%m-%d')
            except (KeyError, ValueError):
                member['graduated_date'] = None

            # for cache
            key = member['position']
            membership = member['membership']

            # cache current
            if membership == 'current':
                if key not in cache_current:
                    cache_current[key] = []
                cache_current[key].append(member)

            # cache alumni
            elif membership == 'alumni':
                if key not in cache_alumni:
                    cache_alumni[key] = []
                cache_alumni[key].append(member)

            # memorize
            members.append(member)
            title2member[member['title']] = member

        # organize data per position (current)
        data_current = OrderedDict()
        current_positions = (
            'Professor',
            'PhD Candidate',
            'PhD Student',
            'Master Student',
            'Intern',
        )
        for position in current_positions:

            # sort members
            if position in cache_current:
                rows = cache_current[position]
                rows = sorted(rows, key=itemgetter('joined_date'), reverse=True)
                data_current[position] = rows

        # organize data per position (alumni)
        data_alumni = OrderedDict()
        alumni_positions = (
            'PhD',
            'Master',
        )
        for position in alumni_positions:

            # sort members
            if position in cache_alumni:
                rows = cache_alumni[position]
                rows = sorted(rows, key=itemgetter('graduated_date'), reverse=True)
                data_alumni[position] = rows

        # memorize
        self.members = members
        self.title2member = title2member
        self.verbose_current_member_data = data_current
        self.verbose_alumni_member_data = data_alumni

    def load_projects(self):

        # prepare
        projects = []

        # for `get_publications_by_project_slug`
        slug2project = {}

        # load
        for fpath in (self.DATA_ROOT / 'projects').glob('*.md'):
            project = parse_metadata(fpath)

            # memorize
            slug2project[project['slug']] = project
            projects.append(project)

        # sort
        projects = sorted(projects, key=itemgetter('date'), reverse=True)

        # memorize
        self.projects = projects
        self.slug2project = slug2project

    def load_publications(self):

        # prepare
        publications = []
        yearset = set()  # all years
        cache = {}

        # load
        for fpath in (self.DATA_ROOT / 'publications').glob('*.md'):
            publication = parse_metadata(fpath)

            # parse year
            year = int(publication['year'])
            yearset.add(year)
            publication['year'] = year

            # parse authors
            authors = parse_list(publication['authors'])
            publication['authors'] = authors

            # memorize member publications
            for title in authors:
                if title not in self.title2member:
                    continue
                member = self.title2member[title]
                if 'publications' not in member:
                    member['publications'] = []
                member['publications'].append(publication)

            # parse projects
            publication['projects'] = parse_list(publication['projects'])

            # memorize project publications
            for slug in publication['projects']:
                if slug not in self.slug2project:
                    continue
                project = self.slug2project[slug]
                if 'publications' not in project:
                    project['publications'] = []
                project['publications'].append(publication)

            # cache
            key = (year, publication['venue_scope'], publication['venue_type'])
            if key not in cache:
                cache[key] = []
            cache[key].append(publication)

            publications.append(publication)

        # sort flattened publications
        publications = sorted(publications, key=itemgetter('date'), reverse=True)

        # sort member publications
        for title in self.title2member:
            member = self.title2member[title]
            if 'publications' not in member:
                member['publications'] = []
            member['publications'] = sorted(member['publications'], key=itemgetter('date'), reverse=True)

        # sort project publications
        for slug in self.slug2project:
            project = self.slug2project[slug]
            if 'publications' not in project:
                project['publications'] = []
            project['publications'] = sorted(project['publications'], key=itemgetter('date'), reverse=True)

        # organize data per year
        data = OrderedDict()
        years = sorted(list(yearset), reverse=True)
        for year in years:

            # organize data per venue scope
            data[year] = OrderedDict()
            venue_scopes = (
                'Global',
                'Domestic',
            )
            for venue_scope in venue_scopes:

                # organize data per venue type
                data[year][venue_scope] = OrderedDict()
                venue_types = (
                    'Conference',
                    'Journal',
                )
                for venue_type in venue_types:

                    # sort publications
                    if (year, venue_scope, venue_type) in cache:
                        rows = cache[(year, venue_scope, venue_type)]
                        rows = sorted(rows, key=itemgetter('date'), reverse=True)
                        data[year][venue_scope][venue_type] = rows

                # in case of empty venue scope
                if not data[year][venue_scope]:
                    del data[year][venue_scope]

            # in case of empty year
            if not data[year]:
                del data[year]

        # memorize
        self.publications = publications
        self.verbose_publication_data = data

    def load_lectures(self):

        # prepare
        lectures = []
        yearset = set()  # all years
        cache = {}

        # load
        for fpath in (self.DATA_ROOT / 'lectures').glob('*.md'):
            lecture = parse_metadata(fpath)

            # parse year
            year = int(lecture['year'])
            yearset.add(year)
            lecture['year'] = year

            # parse assitants
            assitants = parse_list(lecture['assitants'])
            lecture['assitants'] = assitants

            # memorize member lectures
            for title in assitants:
                if title not in self.title2member:
                    continue
                member = self.title2member[title]
                if 'lectures' not in member:
                    member['lectures'] = []
                member['lectures'].append(lecture)

            # cache
            semester = lecture['semester']
            key = (year, semester)
            if key not in cache:
                cache[key] = []
            cache[key].append(lecture)

            lectures.append(lecture)

        # sort member lectures
        for title in self.title2member:
            member = self.title2member[title]
            if 'lectures' not in member:
                member['lectures'] = []
            member['lectures'] = sorted(member['lectures'], key=itemgetter('date'), reverse=True)

        # organize data per year
        data = OrderedDict()
        years = sorted(list(yearset), reverse=True)
        for year in years:

            # organize data per semester
            data[year] = OrderedDict()
            semesters = (
                'Fall',
                'Summer',
                'Spring',
                'Winter',
            )
            for semester in semesters:

                # sort lectures
                if (year, semester) in cache:
                    rows = cache[(year, semester)]
                    rows = sorted(rows, key=itemgetter('date'), reverse=True)
                    data[year][semester] = rows

            # in case of empty year
            if not data[year]:
                del data[year]

        # memorize
        self.lectures = lectures
        self.verbose_lecture_data = data


def get_publications_by_member_title(title):
    db = DB()
    title = str(title).strip()  # just in case
    if title not in db.title2member:
        return []
    return db.title2member[title]['publications']


def get_publications_by_project_slug(slug):
    db = DB()
    slug = str(slug).strip()  # just in case
    if slug not in db.slug2project:
        return []
    return db.slug2project[slug]['publications']


def get_lectures_by_member_title(title):
    db = DB()
    title = str(title).strip()  # just in case
    if title not in db.title2member:
        return []
    return db.title2member[title]['lectures']


def linkify_members(titles):
    titles = parse_list(titles)
    db = DB()
    anchors = []
    for title in titles:
        if title in db.title2member:
            slug = db.title2member[title]['slug']
            anchor = f"<a href='/member/{slug}.html'>{title}</a>"
        else:
            anchor = title
        anchors.append(anchor)
    return ', '.join(anchors)


def add_context(generator, metadata):

    # init
    db = DB()

    # constants
    generator.context['RECENT_DATA_LIMIT'] = generator.settings.get('RECENT_DATA_LIMIT', 5)

    # data
    generator.context['all_headlines'] = db.headlines
    generator.context['all_projects'] = db.projects
    generator.context['all_publications'] = db.publications
    generator.context['verbose_lecture_data'] = db.verbose_lecture_data
    generator.context['verbose_current_member_data'] = db.verbose_current_member_data
    generator.context['verbose_alumni_member_data'] = db.verbose_alumni_member_data
    generator.context['verbose_publication_data'] = db.verbose_publication_data

    # functions
    generator.context['get_publications_by_member_title'] = get_publications_by_member_title
    generator.context['get_publications_by_project_slug'] = get_publications_by_project_slug
    generator.context['get_lectures_by_member_title'] = get_lectures_by_member_title


def add_filters(pelican):

    # prepare
    if 'JINJA_FILTERS' not in pelican.settings:
        pelican.settings['JINJA_FILTERS'] = {}

    # filters
    pelican.settings['JINJA_FILTERS']['linkify_members'] = linkify_members


def register():
    signals.article_generator_context.connect(add_context)
    signals.page_generator_context.connect(add_context)
    signals.initialized.connect(add_filters)
