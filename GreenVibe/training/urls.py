from django.urls import path
from GreenVibeShop import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
   path("training/", views.training),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)