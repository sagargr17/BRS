from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    #    User Apis
    path('userdetail/', UserView.as_view(), name="userview"),
    path('api/token/',  TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/',TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name="sign_up"),


    # Locations Api
    path('locations/', LocationView.as_view()),
    path('location/<int:pk>/', DetailedLocationView.as_view()),
    path('location/<int:pk>/comment', CommentLocationView.as_view()),


    #     Blogs Section
    path('blogs/', BlogView.as_view(), name="Blog"),
    path('createblog/', BlogView.as_view(), name="Blog"),
    path('updateblogs/<int:pk>/', BlogDetail.as_view(), name="Blog"),
    path('blog/<int:pk>/', BlogDetail.as_view(), name="Blog"),

    # comments
    path('location/<int:pk>/comment/',
         CommentLocationView.as_view(), name="commentLocation"),
    path('commentlocation/<int:pk>/delete/',
         DeleteCommentLocationView.as_view(), name="commentLocation"),
    
    
    # Blog Delete 
    path('blog/<int:pk>/comment/', CommentBloggerView.as_view(), name="blog"),
    path('blogcomment/<int:pk>/delete/',
         DeleteCommentBlogView.as_view(), name="blog"),


    # Favouties
    path('favorites/<int:pk>/', LocationFavoritesView.as_view(), name="favorites"),
    path('favorites/', LocationFavoritesView.as_view(), name="favorites"),

     # Repliest
    path('replyLocationComment/<int:pk>/', ReplyLocationComments.as_view(), name="replyComment"),
    path('replyLocationComment/<int:pk>/delete/', ReplyLocationCommentDetail.as_view(), name="replyCommentDelete"),


     #ReplyBlogComment
    path('replyBlogComment/<int:pk>/', ReplyBlogComment.as_view(), name="replyComment"),
    path('replyBlogComment/<int:pk>/delete/', DeleteBlogReplyComment.as_view(), name="deletereplyComment"),
    
    
    path('postlike/<int:pk>/', LikeLocation.as_view(), name="generatingAi"),

    #For RecomendationSystem     
    path('aigenerator/', AiGenerator.as_view(), name="generatingAi"),
    
]
