from django.conf.urls import url
from django.urls import include

from core.presigned_url import PresignedUrl
from core.routes import router
from core.views import EventTypeView, SubscriberReminder, NotificationView

from core.views_layer.invitation import InvitationViewSet


urlpatterns = [
    url('^', include(router.urls)),
    url('presigned-url', PresignedUrl.as_view(), name="image_upload"),
    url('invite', InvitationViewSet.as_view(), name="invite"),
    url("event-type", EventTypeView.as_view(), name="event_type"),
    url('reminder', SubscriberReminder.as_view(), name="subscriber_reminder"),

    url('notification', NotificationView.as_view(), name='notification')
]
