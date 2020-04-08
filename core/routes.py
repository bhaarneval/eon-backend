from rest_framework.routers import DefaultRouter

from core.views_layer.user import UserViewSet
from core.views_layer.events import EventViewSet
from core.views_layer.subscription import SubscriptionViewSet

router = DefaultRouter()
router.register(r'event', EventViewSet)
router.register(r'user', UserViewSet)
router.register(r'subscription', SubscriptionViewSet),
