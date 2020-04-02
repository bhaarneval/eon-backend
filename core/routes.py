from rest_framework.routers import DefaultRouter

from core.views import EventViewSet

router = DefaultRouter()
router.register(r'event', EventViewSet)
