# site
AUTHOR = "theeluwin"
SITENAME = "Pelican Labsite"
SITEURL = "http://theeluwin.github.io/pelican-labsite"
SITEDESCRIPTION = "For building academic lab websites using Pelican."
THEME = 'theme-bootstrap/'
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
RECENT_DATA_LIMIT = 5
GOOGLE_ANALYTICS_ID = ''

# urls
RELATIVE_URLS = False

# contents
PATH = 'content/'

# pages
PAGE_PATHS = ['pages/']
PAGE_SAVE_AS = '{slug}.html'
PAGE_URL = '{slug}.html'

# articles
ARTICLE_PATHS = [
    'data/headlines/',
    'data/lectures/',
    'data/members/',
    'data/projects/',
    'data/publications/',
]
ARTICLE_SAVE_AS = '{category}/{slug}.html'
ARTICLE_URL = '{category}/{slug}.html'

# statics
STATIC_PATHS = [
    'images/',
    'extra/favicon.ico',
    'extra/robots.txt',
]
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/robots.txt': {'path': 'robots.txt'},
}

# plugins
PLUGIN_PATHS = ['plugins/']
PLUGINS = [
    'pelican.plugins.sitemap',
    'labsite.engine',
]

# sitemap
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'pages': 0.5,
        'articles': 0.5,
        'indexes': 0.5,
    },
    'changefreqs': {
        'pages': 'monthly',
        'articles': 'monthly',
        'indexes': 'monthly',
    }
}

# github
GITHUB_RIBBON = False
