from django.urls import path
from .views import *

app_name = 'apps.blog'

urlpatterns = [
    path('my_first_view/', my_first_view),
    path('my_dynamic_url/<path:conv>/', dynamic_view),
    path('vars/<int:var1>/second/<str:var2>/', two_vars),
    path('request_review/', request_review, name='request_review'),

    path('posts/', post_list, name='post_list'),
    path('posts/<int:post_id>/', get_post, name='post_detail'),
    path('posts/<int:post_id>/comments/', get_post_comments, name='comments'),
]
