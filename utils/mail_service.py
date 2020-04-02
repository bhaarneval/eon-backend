import boto3


def send_mail(source=None, receiver=None, message=None, subject=None):
    """
    -send email using ses
    :param receiver:
    :param source:
    :param message:
    :param subject:
    :return:
    """
    client = boto3.client("ses", region_name="us-east-1")
    response = client.send_email(
        Destination={"ToAddresses": receiver},
        Message={
            "Body": {"Text": {"Charset": "UTF-8", "Data": message}},
            "Subject": {"Charset": "UTF-8", "Data": subject},
        },
        Source=source,
    )
