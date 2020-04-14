import boto3
from botocore.config import Config
from django.conf import settings


class AwsS3:
    """
    AWS related services
    """

    def __init__(self):
        self.s3_client = boto3.client("s3", region_name=settings.AWS_REGION,
                                      config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"))

    def get_presigned_url(self, bucket_name, object_name, expiry=3600):
        if not bucket_name:
            return object_name
        response = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiry,
        )
        return response

    def put_presigned_url(self, bucket_name, object_name, expiry=3600):
        response = self.s3_client.generate_presigned_url(
            'put_object',
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiry,
        )
        return response
