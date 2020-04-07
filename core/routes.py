from rest_framework.routers import DefaultRouter

from core.views import UserViewSet
from core.views_layer.events import EventViewSet

router = DefaultRouter()
router.register(r'event', EventViewSet)
router.register(r'user', UserViewSet)
