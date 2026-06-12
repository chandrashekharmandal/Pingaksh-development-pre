import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_presigned_url(s3_key: str, expiry_seconds: int = 900) -> str:
    """
    Generate a pre-signed URL for private S3 objects.

    Args:
        s3_key: The S3 object key (path within the bucket).
        expiry_seconds: How long the URL is valid. Default: 15 minutes.

    Returns:
        A pre-signed HTTPS URL string.
    """
    s3_client = boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": s3_key,
            },
            ExpiresIn=expiry_seconds,
        )
        return url
    except Exception as e:
        logger.error(f"Failed to generate pre-signed URL for {s3_key}: {e}")
        return ""


def generate_presigned_upload_url(
    s3_key: str,
    content_type: str,
    expiry_seconds: int = 300,
) -> dict:
    """
    Generate a pre-signed POST URL for direct client-to-S3 uploads.

    Returns:
        {'url': str, 'fields': dict}
    """
    s3_client = boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, 20 * 1024 * 1024],  # 1B - 20MB
            ],
            ExpiresIn=expiry_seconds,
        )
        return response
    except Exception as e:
        logger.error(f"Failed to generate pre-signed upload URL for {s3_key}: {e}")
        return {}
