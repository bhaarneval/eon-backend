"""
Place you all helper method here
"""
from utils.sms_service import send_sms
from utils.mail_service import send_mail
from core.models import Notification, User, Event
from eon_backend.settings import SMS_CONFIG, EMAIL_CONFIG, NOTIFICATION_CONFIG


def send_email_sms_and_notification(action_name, **kwargs):
    """
    Helper method for sending Email and SMS
    """

    if SMS_CONFIG.get(action_name, {}).get("status"):
        event_dict = SMS_CONFIG.get(action_name)
        send_sms(numbers_list=kwargs["numbers_list"],
                 message=kwargs.get("message") or event_dict["message"])

    if EMAIL_CONFIG.get(action_name, {}).get("status"):
        event_dict = EMAIL_CONFIG.get(action_name)
        send_mail(
            receiver_list=kwargs["email_ids"],
            message=kwargs.get("message") or event_dict["message"],
            subject=kwargs.get("subject") or event_dict["subject"]
        )
    if NOTIFICATION_CONFIG.get(action_name, {}).get("status"):
        event_dict = NOTIFICATION_CONFIG.get(action_name)
        user_ids = kwargs["user_ids"]
        event_id = kwargs["event_id"]
        message = kwargs.get("message") or event_dict["message"]
        users = User.objects.filter(id__in=user_ids)
        event = Event.objects.get(id=event_id)
        for _id in users:
            Notification.objects.create(user=_id, event=event, message=message)
