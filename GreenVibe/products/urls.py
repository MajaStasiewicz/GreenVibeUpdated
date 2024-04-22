from django.urls import path
from GreenVibeShop import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('cart/', views.view_cart),
    path('choice/', views.order_choice),
    path('order/', views.order, name='order'),
    path('cartSummary/', views.cartSummary),
    path('products/<str:category>/', views.products),
    path('moreP/<int:product_id>/', views.moreP),
    #path('codeCheck/', views.codeCheck),
    path('deleteReview/<int:review_id>/', views.deleteReview),
    path('sorting/', views.products),
    path('paySite/', views.paySite, name='paySite'),
    path('pay_submit/', views.pay_submit, name='pay_submit'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)