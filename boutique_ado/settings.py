"""
Django settings for boutique_ado project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'DEVELOPMENT' in os.environ

ALLOWED_HOSTS = ['mattjboland-boutique-ado.herokuapp.com', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'home',
    'products',
    'bag',
    'checkout',
    'profiles',

    # Other
    'crispy_forms',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boutique_ado.urls'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'bag.contexts.bag_contents',
            ],

            # Now normally if you are going to use crispy forms in a couple
            # templates
            # you would just load the template tags like we load static in all
            # our templates.
            # But that becomes tedious if you want to use it all over your
            # application.
            # Instead underneath context processors in the templates setting
            # in settings.py.
            # We can actually add a list called built-ins which will contain
            # all the tags we want available in all our templates by default.
            # from crispy_forms.template_tags we want to add both
            # crispy_forms_tags. And crispy_forms_field.

            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field',
            ]
        },
    },
]

# Lastly we need to add one more setting to
# Settings dot pi to tell it to store messages in the
# session this is often not a required step because there is a default
# which falls back to this storage method but due to the use of git pod
# in these recordings it's required for us

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

WSGI_APPLICATION = 'boutique_ado.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static')),

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

"""To connect Jango to s3 we need to add some settings in settings.py
to tell it which bucket it should be communicating with.
We'll only want to do this on Heroku. So let's add an if statement
to check if there's an environment variable called USE_AWS in the environment.
If so let's define the AWS_STORAGE_BUCKET_NAME
The AWS_S3_REGION_NAME
And our access key, and secret access key, which we'll get from the environment.
It's very important you keep these two keys secret.
Because if they end up in version control someone could use them to store
or move data through your s3 bucket.
And Amazon would bill your credit card for it."""

"""We've now got our static files working correctly so let's handle media files.
First though I'd like to add one optional setting to settings.py called
AWS_S3_OBJECT_PARAMETERS
This will tell the browser that it's okay to cache static files for a long time
since they don't change very often, and this will improve performance for our users.
Everything else we'll need to do is outside of our code.
So let's add that and commit it and push it up to github so it will deploy to Heroku."""

if 'USE_AWS' in os.environ:
    # Cache control
    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    # Bucket Config
    AWS_STORAGE_BUCKET_NAME = 'ckz8780-boutique-ado'
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    """Back in our settings file.
    We need to tell django where our static files will be coming from in production.
    Which is going to be our bucket name.
    .s3.amazonaws.com
    And notice I'm formatting this as an F string so my
    bucket name from above will be interpreted and added to generate the appropriate URL"""

    # Static and media files
    """The last step then is to go to Settings.py
    Tell it that for static file storage we want to use our storage class we just created.
    And that the location it should save static files is a folder called static.
    And then do the same thing for media files by using the default file storage.
    And media files location settings."""

    STATICFILES_STORAGE = 'custom_storages.StaticStorage'
    STATICFILES_LOCATION = 'static'
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
    MEDIAFILES_LOCATION = 'media'

    # Override static and media URLs in production
    """We also need to override and explicitly set the URLs for static and media
    files. Using our custom domain and the new locations."""

    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'

    """What happens now is when our project is deployed to Heroku.
    Heroku will run python3 manage.py collectstatic during the build process.
    Which will search through all our apps and project folders looking for static
    files. And it will use the s3 custom domain setting here
    in conjunction with our custom storage classes that tell it the location at
    that URL. Where we'd like to save things.
    So in effect when the USE_AWS setting is true.
    Whenever collectstatic is run.
    Static files will be collected into a static folder in our s3 bucket.
    The beauty of this is that it's all automatic.
    To make sure it works, all we have to do is add all these changes. Commit them.
    And then issue a git push. Which will trigger an automatic deployment to
    Heroku. With that done if we look at the build log.
    We can see that all the static files were collected successfully.
    And if we now go to s3.
    We can see we have a static folder in our bucket with all our static files in
    it. In the next video, we'll upload our product images to s3
    And put the finishing touches on our deployment."""

# Stripe

"""First I'll add a setting called STRIPE_CURRENCY which for the moment will
have a value of usd.
These next two are important. The first one is STRIPE_PUBLIC_KEY
And we'll want to get this from the environment giving it an empty
default value. The same is true for STRIPE_SECRET_KEY.
The reason we're getting these from the environment
is because even though the public key is already in our github from the
last commit. We really don't want the secret key in there because the
secret key can be used to do everything on stripe including creating
charges making payments, issuing refunds, and even updating our own
account information. So it's really important to keep the secret key
safe and out of version control.
The public key is meant to be public so that doesn't really matter.
But for consistency, I'm adding it here anyway."""

FREE_DELIVERY_THRESHOLD = 50
STANDARD_DELIVERY_PERCENTAGE = 10
STRIPE_CURRENCY = 'usd'
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WH_SECRET = os.getenv('STRIPE_WH_SECRET', '')

# The last thing we need to do is add the DEFAULT_FROM_EMAIL to settings.py

DEFAULT_FROM_EMAIL = 'boutiqueado@example.com'

"""The last step then is just to add a few settings to settings.py
Let's follow a similar procedure to our other settings here,
where we check if development is in os.environ.
To determine which email setup to use.
If that variable is set, we'll log emails to the console.
And the only setting we need to specify is the default from email.
And that will be boutiqueado@example.com
Otherwise, for production we'll need to set several variables.
EMAIL_BACKEND, which will be set to django.core.mail.backends.smpt.EmailBackend
EMAIL_USE_TLS which will be true
EMAIL_PORT which will be port 587
EMAIL_HOST which will be smtp.gmail.com
And then the username, password, and DEFAULT_FROM_EMAIL
all of which will get from the environment.
With that finished to complete the set up we just need to deploy to Heroku.
Which can be done by adding all our changes.
Committing.
And then issuing a git push
To test it out let's head to our Heroku app. And try to register for an account.
I'll use a temporary email from tempmail.org
So I've got the confirmation email which means email is being sent properly.
And now I can verify my account.
And I'm able to login."""


if 'DEVELOPMENT' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # this from line 129
    DEFAULT_FROM_EMAIL = 'boutiqueado@example.com'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASS')
    DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')
