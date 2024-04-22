from django.urls import path
from GreenVibeShop import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('survey/', views.surveyHomePage, name='surveyHomePage'),   
    path("data/", views.data),  
    path("question/", views.questionBeggining), 
    path("questionCheck/", views.questionBeggining), 
    path("heading/", views.heading), 
    path("check/", views.checkboxes),
    path("WŁOSYIPAZNOKCIE/", views.next),
    path("ENERGIAISEN/", views.next),
    path("PAMIĘĆISKUPIENIE/", views.next),
    path("KOŚCIISTAWY/", views.next),
    path("ODPORNOŚĆ/", views.next),
    path("STRES/", views.next),
    path("OGÓLNEZDROWIE/", views.next),
    path("saving/", views.saving),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)