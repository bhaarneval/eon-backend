"""
SMS service Configuration
"""
import boto3

from eon_backend.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, TOPIC_NAME


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

    # Create the topic if it doesn't exist (this is idempotent)
    topic = client.create_topic(Name=TOPIC_NAME)
    topic_arn = topic['TopicArn']  # get its Amazon Resource Name

    sms_attrs = {
        'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}
    }

    # Add SMS Subscribers
    for number in numbers_list:
        client.subscribe(
            TopicArn=topic_arn,
            Protocol='sms',
            Endpoint=number  # <-- number who'll receive an SMS message.
        )

    # Publish a message.
    client.publish(Message=message, TopicArn=topic_arn, MessageAttributes=sms_attrs)
