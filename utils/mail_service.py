import boto3
from botocore.exceptions import ClientError

from eon_backend.settings import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                                  AWS_REGION, EMAIL_ID)


def send_mail(receiver_list=None, message=None, subject=None):
    """
    -send email using ses
    :param receiver_list: list of email_addresses
    :param message: message to be send
    :param subject: Subject for the mail
    :return:
    """
    client = boto3.client(
        "ses",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    try:
        for receiver in receiver_list:
            client.send_email(
                Destination={"ToAddresses": [receiver]},
                Message={
                    "Body": {"Text": {"Charset": "UTF-8", "Data": message}},
                    "Subject": {"Charset": "UTF-8", "Data": subject},
                },
                Source=EMAIL_ID,
            )
    except ClientError as e:
        pass
