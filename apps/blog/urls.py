from django.urls import path
from .views import *

app_name = 'apps.blog'

urlpatterns = [

    # path('posts/', post_list, name='post_list'), # FBV
    path('posts/', PostListView.as_view(), name='post_list'),  # CBV аналог

    # path('posts/<int:post_id>/', get_post, name='post_detail'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    # path('posts/<int:post_id>/comments/', get_post_comments, name='comments'),
    path('posts/<int:post_id>/comments/', CommentListView.as_view(), name='comments'),

    path('posts/create/', PostCreateView.as_view(), name='post_create')
]
