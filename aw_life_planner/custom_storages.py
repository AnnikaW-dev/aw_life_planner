# custom_storages.py - More explicit custom storage classes

from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Custom storage for static files"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True

    # Override methods that cause filesystem issues
    def path(self, name):
        raise NotImplementedError(
            "This backend doesn't support absolute paths."
            )


class MediaStorage(S3Boto3Storage):
    """Custom storage for media files"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
