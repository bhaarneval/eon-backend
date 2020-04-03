from django.conf.urls import url
from django.urls import include
from core.routes import router
from core.views import SubscriptionViewSet

urlpatterns = [
    url('^', include(router.urls)),
    url('subscription', SubscriptionViewSet.as_view(), name="subscription")
]
