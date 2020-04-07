from rest_framework.routers import DefaultRouter

from core.views import EventViewSet, UserViewSet

router = DefaultRouter()
router.register(r'event', EventViewSet)
router.register(r'user', UserViewSet)
