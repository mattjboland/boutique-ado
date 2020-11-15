from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

"""The next step is to tell django that in production
we want to use s3 to store our static files whenever someone runs collectstatic.
And that we want any uploaded product images to go there also.
To do that let's create a file called custom storages.
And import both our settings from django.conf
As well as the s3boto3 storage class from django storages which we just installed.
Now I can create a custom class called static storage.
Which will inherit the one from django storages. Giving it all its functionality.
And tell it that we want to store static files in a location from the settings that we'll define in just a moment.
I'll copy this to another class for media files which will have an identical structure.
Had an issue deploy so added this lie to retry"""


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
