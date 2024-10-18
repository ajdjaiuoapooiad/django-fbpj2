from django.shortcuts import render
from django.core.paginator import Paginator

from core.models import VISIBILITY, Post


def index(request):
    posts = Post.objects.filter(active=True, visibility="Everyone")

    context = {
        "posts":posts
    }
    return render(request, "core/index.html", context)