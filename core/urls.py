from django.urls import include, path

from core import  views

app_name = "core"

urlpatterns = [
    path('', views.index,name='feed'),
    path('create-post/',views.create_post,name='create-post'),
    path("like-post/", views.like_post, name="like-post"),
    path("comment-post/", views.comment_on_post, name="comment-post"),
    path("like-comment/", views.like_comment, name="like-comment"),
    path("reply-comment/", views.reply_comment, name="reply-comment"),
    path("delete-comment/", views.delete_comment, name="delete-comment"),


]