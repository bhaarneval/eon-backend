from django.conf.urls import url
from django.urls import include
from core.routes import router


urlpatterns = [
    url('^', include(router.urls))
]
