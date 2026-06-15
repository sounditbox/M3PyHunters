from django.urls import path
from .views import *

app_name = 'apps.blog'
urlpatterns = [

    # path('posts/', post_list, name='post_list'), # FBV
    # path('posts/<int:post_id>/', get_post, name='post_detail'),
    # path('posts/<int:post_id>/comments/', get_post_comments, name='comments'),

    path('posts/create/', PostCreateView.as_view(), name='post_create'), # CBV аналог
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/update', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:post_id>/comments/', CommentListView.as_view(),
         name='comments'),

]

