from django.conf.urls import url
from django.urls import include
from django.views.decorators.csrf import csrf_exempt

from core.presigned_url import PresignedUrl
from core.routes import router
from core.views import SubscriptionViewSet

urlpatterns = [
    url('^', include(router.urls)),
    url('subscription', SubscriptionViewSet.as_view(), name="subscription"),
    url('presigned-url', PresignedUrl.as_view(), name="image_upload")
]
