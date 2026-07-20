from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, reverse_lazy

from apps.users.forms import LoginForm
from apps.users.views import RegisterView, ProfileView, \
    EditProfileView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='users/login.html',
        form_class=LoginForm,
        redirect_field_name='next'
    ), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('blog:post_list')), name='logout'),

    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>', EditProfileView.as_view(), name='edit'),
]
