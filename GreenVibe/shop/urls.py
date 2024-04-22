
from django.urls import path
from . import views
from .views import PasswordsChangeView, PasswordsResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('home/', views.index),
    path('homeCopy/', views.home),
    path('aboutUs/', views.aboutUs),
    path('contact/', views.contact),
    path('rules/', views.rules),
    path('pay/', views.pay),
    path('returns/', views.returns),
    path('newsletter/', views.newsletter),
    path('login/', views.loginSite),
    path('loginSiteCart/', views.loginSiteCart),
    path('register/', views.register),
    path('logout/', views.logoutSite),
    path('change/', PasswordsChangeView.as_view(template_name='change.html')),
    path('passwordSuccess/', views.password_success, name="password_success"),
    path('accountShop/', views.accountShop),
    path('saveBlank/', views.saveBlank),
    path('delete_account/', views.delete_account),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reward/<str:parametr>/', views.reward),

    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),name='reset_password'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'),name='password_reset_sent'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_conf.html'),name='password_reset_conf'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_compl.html'),name='password_reset_compl'),
]

from .views import (
    handler404, handler500, handler403,
    handler400, handler401, handler503,
    handler429, handler502, handler504
)

handler404 = handler404
handler500 = handler500
handler403 = handler403
handler400 = handler400
handler401 = handler401
handler503 = handler503
handler429 = handler429
handler502 = handler502
handler504 = handler504