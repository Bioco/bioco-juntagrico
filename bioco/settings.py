# Django settings for bioco project.
import os
import dj_database_url

"""
    General Settings
"""
DEBUG = os.environ.get("JUNTAGRICO_DEBUG", "True") == "True"

DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

ALLOWED_HOSTS = [
    'intranet.bioco.ch',
    'intranet-new.bioco.ch',
    'intranet-test.bioco.ch',
    'intranet-old.bioco.ch',
    'bioco.juntagrico.science',
    'bioco.herokuapp.com',
    'bioco-new.herokuapp.com',
    'bioco-test.herokuapp.com',
    'bioco-old.herokuapp.com',
]
if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1']

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

FILE_UPLOAD_PERMISSIONS = 0o444

ROOT_URLCONF = 'bioco.urls'

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGIN_REDIRECT_URL = "/my/home"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bioco.wsgi.application'

SECRET_KEY = os.environ.get('JUNTAGRICO_SECRET_KEY')

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

OAUTH2_PROVIDER = {
    'SCOPES': {
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'bioco/templates'
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
            'debug' : True
        },
    },
]


MIDDLEWARE=[
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #'subdomains.middleware.SubdomainURLRoutingMiddleware',
    #'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

INSTALLED_APPS = (
    'juntagrico',
    'bioco',
    'polymorphic',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'juntagrico_billing',
    #'juntagrico_pg',
    #'juntagrico_polling',
    #'juntagrico_webdav',
    'crispy_forms',
    'impersonate',
    #'oauth2_provider',
    'oidc_provider',
    'adminsortable2',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)



"""
    Logging Settings
"""
if os.environ.get("BIOCO_LOGGING"):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                           'pathname=%(pathname)s lineno=%(lineno)s ' +
                           'funcname=%(funcName)s %(message)s'),
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }


"""
    Email Settings
"""
WHITELIST_EMAILS = []
def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email.replace('@gmail.com', '(\+\S+)?@gmail.com'))

whitelist_email_from_env("JUNTAGRICO_EMAIL_USER")

if DEBUG is True:
    for key in list(os.environ.keys()):
        if key.startswith("JUNTAGRICO_EMAIL_WHITELISTED"):
            whitelist_email_from_env(key)

EMAIL_HOST = os.environ.get('JUNTAGRICO_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('JUNTAGRICO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('JUNTAGRICO_EMAIL_PASSWORD')
EMAIL_PORT = int(os.environ.get('JUNTAGRICO_EMAIL_PORT', '587' ))
EMAIL_USE_TLS = os.environ.get('JUNTAGRICO_EMAIL_TLS', 'False')=='True'
EMAIL_USE_SSL = os.environ.get('JUNTAGRICO_EMAIL_SSL', 'False')=='True'


"""
    Admin Settings
"""
ADMINS = [
    ('Admin', os.environ.get('JUNTAGRICO_ADMIN_EMAIL')),
]
MANAGERS = ADMINS
SERVER_EMAIL="intranet@bioco.ch"

"""
    Auth Settings
"""
AUTHENTICATION_BACKENDS = (
    'juntagrico.util.auth.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend',
    #'oauth2_provider.backends.OAuth2Backend',
)

"""
    DB Settings
"""
DATABASES = {'default': {}}
if os.environ.get('JUNTAGRICO_DATABASE_ENGINE'):
    DATABASES['default'] = {
            'ENGINE': os.environ.get('JUNTAGRICO_DATABASE_ENGINE','django.db.backends.sqlite3'),
            'NAME': os.environ.get('JUNTAGRICO_DATABASE_NAME','bioco.db'),
            'USER': os.environ.get('JUNTAGRICO_DATABASE_USER'), #''junatagrico', # The following settings are not used with sqlite3:
            'PASSWORD': os.environ.get('JUNTAGRICO_DATABASE_PASSWORD'), #''junatagrico',
            'HOST': os.environ.get('JUNTAGRICO_DATABASE_HOST'), #'localhost', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': os.environ.get('JUNTAGRICO_DATABASE_PORT', False), #''', # Set to empty string for default.
        }
else:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

"""
    Caching  Settings
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'oooo_cache_table',
        'TIMEOUT': None,
    }
}

"""
    Localization Settings
"""
TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'de'

USE_I18N = True

USE_L10N = True

DATE_INPUT_FORMATS =['%d.%m.%Y',]

USE_TZ = True


"""
    Static Settings
"""
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = ( 
    os.path.join(BASE_DIR, 'static_general'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

"""
    Impersonate Settings
"""
IMPERSONATE = {
    'REDIRECT_URL': '/my/profile',
}

"""
    File & Storage Settings
"""
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
MEDIA_ROOT = 'media/'

if os.environ.get('JUNTAGRICO_AWS_KEY_ID'):
    try:
         AWS_ACCESS_KEY_ID = os.environ['JUNTAGRICO_AWS_KEY_ID']
         AWS_SECRET_ACCESS_KEY = os.environ['JUNTAGRICO_AWS_KEY']
         AWS_STORAGE_BUCKET_NAME = os.environ['JUNTAGRICO_AWS_BUCKET_NAME']
    except KeyError:
         raise KeyError('Need to define AWS environment variables: ' +
                        'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_STORAGE_BUCKET_NAME')

      # Default Django Storage API behavior - don't overwrite files with same name
    AWS_S3_FILE_OVERWRITE = False

    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_PUBLIC_MEDIA_LOCATION = 'media'

    DEFAULT_FILE_STORAGE = 'bioco.storage_backends.PublicMediaStorage'

    MEDIA_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_STORAGE_BUCKET_NAME, AWS_PUBLIC_MEDIA_LOCATION)
else:
    # not using AWS, e.g. when testing locally
    pass

    # using FTP:
    # DEFAULT_FILE_STORAGE = 'storages.backends.ftp.FTPStorage'
    # FTP_STORAGE_LOCATION = os.environ.get('JUNTAGRICO_FTP_STORAGE_LOCATION')

"""
     Crispy Settings
"""
CRISPY_TEMPLATE_PACK = 'bootstrap4'

"""
    Subdomain Settings
"""
# A dictionary of urlconf module paths, keyed by their subdomain.
'''SUBDOMAIN_URLCONFS = {
    None: 'bioco.urls', 
    'www': 'bioco.urls',
    'intranet': 'bioco.urls',
    'my': 'bioco.myurlsredirect',
    'bioco': 'fuckoff'
}
'''

"""
    Juntagrico Settings
"""
VOCABULARY = {
    'member': 'biocò',
    'member_pl': 'biocòs',
    'assignment': 'Rüebli',
    'assignment_pl': 'Rüebli',
    'share': 'Anteilschein',
    'share_pl': 'Anteilscheine',
    'subscription': 'Abo',
    'subscription_pl': 'Abos',
    'co_member': 'MitabonnentIn',
    'co_member_pl': 'MitabonnentInnen',
    'price': 'Betriebsbeitrag',
    'member_type': 'Mitglied',
    'member_type_pl': 'Mitglieder',
    'depot': 'Depot',
    'depot_pl': 'Depots',
    'package': 'Korb',
    'ombudsman_contact': os.environ.get('BIOCO_OMBUDSMAN_CONTACT'),
    'finance_contact': os.environ.get('BIOCO_FINANCE_CONTACT'),
}

ORGANISATION_NAME = "biocò"
ORGANISATION_LONG_NAME = "biocò - Gemüsegenossenschaft Region Baden Brugg"
ORGANISATION_ADDRESS = {
    "name": "Gemüsegenossenschaft biocò",
    "street": "Allmendstrasse",
    "number": "39b",
    "zip": "5400",
    "city": "Baden",
    "extra": "c/o Anna Zehnder"
}
ORGANISATION_BANK_CONNECTION = {
    "PC": "46-110-7",
    "IBAN": "CH80 0839 0032 9330 1010 5",
    "BIC": "ABSOCH22",
    "NAME": "Alternative Bank Schweiz AG"
}
INFO_EMAIL = "info@bioco.ch"
SERVER_URL = "www.bioco.ch"
ADMINPORTAL_NAME = "biocò Intranet"
ADMINPORTAL_SERVER_URL = "intranet.bioco.ch"
BUSINESS_REGULATIONS = "https://bioco.ch/wp-content/uploads/2018/12/1812_bioco_Betriebsreglement.pdf"
BYLAWS = "https://bioco.ch/wp-content/uploads/2017/01/1701-Statuten.pdf"
MAIL_TEMPLATE = "bioco_email.html"
STYLES = {'static': ['css/bioco.css']}
FAVICON = "/static/img/bioco_favicon.png"
FAQ_DOC = "" # we dont have an FAQ, emtpy will not show
EXTRA_SUB_INFO = "" # we dont have a Zusatzabos, emtpy will not show
ACTIVITY_AREA_INFO = "" # we dont have Taetigkeitsbereich Infos, emtpy will not show
SHARE_PRICE = "250"
PROMOTED_JOB_TYPES = ["Aktionstag"]
PROMOTED_JOBS_AMOUNT = 2
DEPOT_LIST_GENERATION_DAYS = [1, 4] # 0 = Monday
BUSINESS_YEAR_START = {"day":1, "month":1}
BUSINESS_YEAR_CANCELATION_MONTH = 9
DEMO_USER = ''
DEMO_PWD = ''
IMAGES = {  'status_100': '/static/img/status_100.png',
            'status_75': '/static/img/status_75.png',
            'status_50': '/static/img/status_50.png',
            'status_25': '/static/img/status_25.png',
            'status_0': '/static/img/status_0.png',
            'single_full': '/static/img/ruebli_color.png',
            'single_empty': '/static/img/ruebli_bw.png',
            'single_core': '/static/img/ruebli_color.png', # not distinguishing core and non-core
            'core': '/static/img/ruebli_bw.png',  # not distinguishing core and non-core
            'job_occupied': '/static/img/erbse_voll.png',
            'job_free': '/static/img/erbse_leer.png',
            'job_multiplier': '/static/img/ruebli_color.png',
}
DEFAULT_MAILER = 'bioco.mailer.Mailer'

OIDC_USERINFO = 'bioco.oidc_provider_settings.userinfo'
OIDC_EXTRA_SCOPE_CLAIMS = 'bioco.oidc_provider_settings.CustomScopeClaims'

FROM_FILTER = {'filter_expression': '.*@bioco\.ch',
               'replacement_from': 'intranet@bioco.ch'}

from juntagrico.util import addons
addons.config.register_user_menu('bioco_menu.html')
#addons.config.register_admin_menu('bioco_admin_menu.html')
