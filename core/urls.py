from django.conf.urls import url
from django.urls import include

from core.presigned_url import PresignedUrl
from core.routes import router
from core.views_layer.subscription import SubscriptionViewSet

urlpatterns = [
    url('^', include(router.urls)),
    url('subscription', SubscriptionViewSet.as_view(), name="subscription"),
    url('presigned-url', PresignedUrl.as_view(), name="image_upload")
]
