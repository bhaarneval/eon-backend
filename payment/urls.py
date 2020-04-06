from django.conf.urls import url
from payment.views import PaymentViewSet

urlpatterns = [
    url('', PaymentViewSet.as_view(), name="payment"),
]
