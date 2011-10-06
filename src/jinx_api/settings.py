# Django settings for jinx_api project.

# Initialize connection to clusto database:
import clusto.scripthelpers
import os
import re
clusto.scripthelpers.init_script()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# load global settings from jinx.conf
# if this variable is passed in from some external, non-local invocation, respect the 
# passed conf file location, which is relative to the local directory.  Otherwise, set 
# the location of the config file to the correct one relative to settings.py

class ConfigurationError(ValueError):
    pass

jinx_settings = os.environ.get("JINX_CONF_FILE", "/etc/jinx/jinx.conf")

jinx_global_settings={}

if os.path.exists(jinx_settings):
    try:
        f = open(jinx_settings)
    except IOError, e:
        raise ConfigurationError("Cannot open jinx settings %s - %s" % (jinx_settings, e.strerror))
    for l in f:
        m = re.search(r'^[^#]*?([\w_]+)="?([^"]+)"?\s*;?\s*$', l)
        if m:
            jinx_global_settings[m.group(1)] = m.group(2).strip()
    f.close
else:
    print ("Cannot find jinx settings %s" % jinx_settings)
    sys.exit(1)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
DATABASE_ENGINE = jinx_global_settings['DB_JINX_DATABASE_ENGINE'] # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = jinx_global_settings['DB_JINX_DATABASE_NAME'] # Or path to database file if using sqlite3.
DATABASE_USER = jinx_global_settings['DB_JINXUSER']           # Not used with sqlite3.
DATABASE_PASSWORD = jinx_global_settings['DB_JINXUSER_PWD']  # Not used with sqlite3.
DATABASE_HOST = jinx_global_settings['DB_JINX_DATABASE_HOST']  # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
if DATABASE_ENGINE == "mysql":
    DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB",}

# ldap configuration settings. 

LDAP_SERVER='ldaps://ldap-a.lindenlab.com/'
LDAP_SEARCH_TREE='ou=group,dc=lindenlab,dc=com'
LDAP_FILTER='(cn=ops)'
LDAP_FIELD='memberUid'
LDAP_PASSWD='1loveld4p'
LDAP_BIND_DN='cn=unix,ou=system,dc=lindenlab,dc=com'
ALL_USERS_GROUP=1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p8#i)t3+xcz&#x)%nqfu$r8)n9pxoi8r7^#op&(_rhplrq-t4n'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'jinx_api.middleware.APIDocumentationMiddleware',
    'jinx_api.middleware.JinxAuthorizationMiddleware',
    'jinx_api.middleware.JSONMiddleware',
    
)

AUTHENTICATION_BACKENDS = (
        'jinx_api.LdapRemoteUserBackend.LDAPRemoteUserBackend',
#        'django.contrib.auth.backends.RemoteUserBackend',
       )

# User profiles
AUTH_PROFILE_MODULE = 'api.UserProfile'

ROOT_URLCONF = 'jinx_api.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
#    os.path.join(PROJECT_PATH, 'api', 'templates'),
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

INSTALLED_APPS = (
    'jinx_api.api',
    'jinx_api.ui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_nose',
#    'django.contrib.messages',
    # Uncomment the next line to enable the admin:

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)


