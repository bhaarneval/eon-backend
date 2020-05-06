import os

# AWS
BUCKET = os.environ.get('BUCKET_NAME')
BUCKET_PATH = os.environ.get('AWS_BUCKET_PATH')
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
EMAIL_ID = os.environ.get("EMAIL_ID")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
