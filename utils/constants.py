"""
All related constants are here
"""
PAYMENT_CONSTANTS = dict(
    status=[(0, "CREDIT"), (3, "REFUND")],
    values=dict(
        status=dict(CREDIT=0, REFUND=3),
    ),
)
APPLICATION_CONSTANTS = dict(transaction=PAYMENT_CONSTANTS)

DEFAULT_PASSWORD = dict(password='default')

SMS_CONFIG = {
    "invitation_send": {"status": True,
                        "message": "You are invited to subscribe for '{event_name}' "
                                   "event with {discount_percentage}% discount by "
                                   "the event organizer."},
    "invitation_delete": {"status": True,
                          "message":
                              "You have been removed from invitation list of '{event_name}' event "
                              "by the event organizer."}
}

EMAIL_CONFIG = {
    "user_created": {"status": False,
                     "message": "Thank you for registering with BITS-EOn.",
                     "subject": "Registration successful"},
    "change_password": {"status": False,
                        "message": "Your password is changed recently.",
                        "subject": "Password changed"},
    "event_updated": {"status": True,
                      "message": "The {field} of your subscribed event '{event_name}' has been changed "
                                 "by the organizer from {prev_value} to {next_value}.",
                      "subject": "Subscribed event updated"},
    "event_deleted": {"status": True,
                      "message": "Your subscribed event '{event_name}' is deleted "
                                 "by the organizer because {message}. "
                                 "Your amount is initiated for refund.",
                      "subject": "Subscribed event cancelled"},
    "event_reminder": {"status": True,
                       "message": "This mail is just a reminder for your subscribed event"
                                  " '{event_name}' from the event organizer with a note for"
                                  " you.\n'{message}'.",
                       "subject": "Registered event reminder"},
    "invitation_send": {"status": True,
                        "message": "You are invited for '{event_name}' event with {discount_percentage}% discount. "
                                   "Please subscribe for this event here {url}",
                        "subject": "Invitation for an event"},
    "invitation_delete": {"status": True,
                          "message": "You have been removed from the invitation list of '{event_name}' event.",
                          "subject": "Invitation cancelled for the event"},
    "user_share": {"status": True,
                   "message": "'{message}'\nYour friend is going for the "
                              "'{event_name}' event asking you to"
                              " join along with him. Please subscribe for this {url}",
                   "subject": "Join this exciting event with your friend"},
    "forget_password": {"status": True,
                        "message":
                            "The verification code for changing password is {verification_code}",
                        "subject": "Verification code to reset password"},
    "send_updates": {"status": True,
                     "message": "Event Organizer for the '{event_name}' event "
                                "has sent a note for you.\n '{message}'.",
                     "subject": "Subscribed event updates"},
}

NOTIFICATION_CONFIG = {
    "event_updated": {"status": True,
                      "message": "The {field} of your subscribed event "
                                 "'{event_name}' has been changed "
                                 "by the organizer from {prev_value} to {next_value}."},
    "event_deleted": {"status": True,
                      "message": "Your subscribed event '{event_name}' "
                                 "is deleted by the organizer because {message}. "
                                 "Your amount is initiated for refund."},
    "event_reminder": {"status": True,
                       "message": "Reminder for '{event_name}' event from the organizer "
                                  "with a note for you.\n'{message}'."},
    "send_updates": {"status": True,
                     "message": "Update for '{event_name}' event from the event organizer "
                                "with a note for you.\n'{message}'."}
}

EVENT_STATUS_DEFAULT = 'upcoming'
EVENT_STATUS_COMPLETED = 'completed'
EVENT_STATUS_CANCELLED = 'cancelled'

SUBSCRIPTION_TYPE_DEFAULT = 'all'
SUBSCRIPTION_TYPE_FREE = 'free'
SUBSCRIPTION_TYPE_PAID = 'paid'