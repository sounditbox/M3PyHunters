from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, reverse_lazy

from apps.users.forms import LoginForm
from apps.users.views import register_view

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='users/login.html',
        form_class=LoginForm
    ), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('blog:post_list')), name='logout'),
]
