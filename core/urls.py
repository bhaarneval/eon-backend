from django.conf.urls import url
from django.urls import include

from core.presigned_url import PresignedUrl
from core.routes import router
from core.views import SubscriptionViewSet, EventTypeView, SubscriberReminder

urlpatterns = [
    url('^', include(router.urls)),
    url('subscription', SubscriptionViewSet.as_view(), name="subscription"),
    url('presigned-url', PresignedUrl.as_view(), name="image_upload"),
    url("event-type", EventTypeView.as_view(), name="event_type"),
    url('reminder', SubscriberReminder.as_view(), name="subscriber_reminder")
]
