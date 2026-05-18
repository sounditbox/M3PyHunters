from django.urls import path
from .views import my_first_view

app_name = 'blog'

urlpatterns = [
    path('my_first_view/', my_first_view),
]
