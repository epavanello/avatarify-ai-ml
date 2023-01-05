
import boto3
from boto3.s3.transfer import TransferConfig, S3Transfer

def getS3Client():
    myconfig = TransferConfig(
        multipart_threshold=9999999999999999,
        max_concurrency=10,
        num_download_attempts=10,
    )

    s3 = boto3.client("s3")


    return S3Transfer(s3, myconfig)