from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """
    S3 storage for uploaded media files.
    """
    location = ''
    file_overwrite = False