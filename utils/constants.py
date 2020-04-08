PAYMENT_CONSTANTS = dict(
    status=[(0, "SUCCESSFUL"), (1, "FAILED"), (2, "IN_PROGRESS"), (3, "REFUND")],
    values=dict(
        status=dict(SUCCESSFUL=0, FAILED=1, IN_PROGRESS=2, DECLINED=3),
    ),
)
APPLICATION_CONSTANTS = dict(transaction=PAYMENT_CONSTANTS)

DEFAULT_PASSWORD = dict(password='default')

SMS_CONFIG = {
    "invitation": {"status": True,
                   "message": "You are invited for the event. Please registered to avail the discount for the event."}
}

EMAIL_CONFIG = {
    "user_created": {"status": True,
                     "message": "Thank you for registering with BITS-EOn.",
                     "subject": "REGISTRATION SUCCESSFUL"},
    "change_password": {"status": True,
                        "message": "Your password is changed recently.",
                        "subject": "PASSWORD CHANGED"},
    "event_updated": {"status": True,
                      "message": "Your registered event is modified by the organiser.",
                      "subject": "EVENT UPDATED"},
    "event_deleted": {"status": True,
                      "message": "Your registered event is deleted by the organiser.",
                      "subject": "REGISTERED EVENT DELETED"},
    "event_reminder": {"status": True,
                       "message": "Reminder for the registered event.",
                       "subject": "REGISTERED EVENT REMINDER"},
    "invitation": {"status": True,
                   "message": "You are invited for the event. Please registered to avail the discount for the event.",
                   "subject": "INVITATION FOR AN EVENT"},
    "user_share": {"status": True,
                   "message": "Your friend is going for the event asking you to join along with him.",
                   "subject": "JOIN THIS EXCITING EVENT WITH YOUR FRIEND."}
}

NOTIFICATION_CONFIG = {
    "event_updated": {"status": True,
                      "message": "Your registered event is modified by the organiser."},
    "event_deleted": {"status": True,
                      "message": "Your registered event is deleted by the organiser."},
    "event_reminder": {"status": True,
                       "message": "Reminder for the registered event."}
}
