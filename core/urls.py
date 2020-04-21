"""
In this file we added all the url reference
"""
from django.conf.urls import url
from django.urls import include

from core.presigned_url import PresignedUrl
from core.routes import router
from core.views import get_event_types, SubscriberNotify, send_mail_to_a_friend, get_event_summary
from core.views_layer.invitation import InvitationViewSet
from core.views_layer.notification import NotificationView
from core.views_layer.feedback import get_feedback_questions, FeedbackView

urlpatterns = [
    url('^', include(router.urls)),
    url('presigned-url', PresignedUrl.as_view(), name="image_upload"),
    url(r'^invite', InvitationViewSet.as_view(), name="invite"),
    url('notify-subscriber', SubscriberNotify.as_view(), name="subscriber_notify"),
    url("event-type", get_event_types, name="event_type"),
    url("share-with-friend", send_mail_to_a_friend, name="share_with_friend"),
    url('notification', NotificationView.as_view(), name='notification'),
    url(r'^event-summary', get_event_summary, name="event_summary"),
    url(r'feedback-questions', get_feedback_questions, name="feedback_questions"),
    url('feedback', FeedbackView.as_view(), name="feedback")
]
