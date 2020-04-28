"""
SMS service Configuration
"""
import boto3

from eon_backend.settings.common import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION


def send_sms(numbers_list, message):
    """
        -send SMS using SNS

    """
    # Create an SNS client
    client = boto3.client(
        "sns",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    sms_attrs = {
        'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}
    }

    # Add SMS Subscribers
    for number in numbers_list:
        client.publish(
            PhoneNumber=number,
            Message=message,
            MessageAttributes=sms_attrs
        )
