from django.urls import path
from GreenVibeShop import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("blog/", views.blog),    
    path("ranking/", views.ranking), 
    path("accountBlog/", views.account), 
    path("noaccount/", views.noaccount), 
    path("postCreate/", views.postCreate), 
    path("more/<int:post_id>/", views.more),
    path("comment/<int:post_id>/", views.comment), 
    path("allPosts/", views.allPosts),
    path("myPosts/", views.myPosts),
    path("deletePost/<int:post_id>/", views.deletePost),
    path("deleteReviewBlog/<int:post_id>/", views.deleteReview),
    path("deleteAnswer/<int:post_id>/", views.deleteAnswer),
    path("avatarChange/<int:user_id>/", views.avatarChange),
    path("answerReview/<int:post_id>/", views.answerReview),
    path("messenger/", views.messenger),
    path("roomShow/<int:room_id>/", views.roomShow),
    path("send/", views.send, name='send'),
    path('getMessages/<int:room_id>/', views.getMessages),
    path("planner/", views.planner),
    path("plannerSave/", views.plannerSave),
    path("deletePlanner/", views.deletePlanner),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)