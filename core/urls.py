from django.urls import include, path

from core import  views

app_name = "core"

urlpatterns = [
    path('', views.index,name='feed'),
    path('create-post/',views.create_post,name='create-post'),
]