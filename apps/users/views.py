from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from apps.users.forms import RegistrationForm, EditProfileForm


class RegisterView(CreateView):
    model = get_user_model()
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'users/profile.html'
    context_object_name = 'user'
    queryset = (
        get_user_model().objects
        .all()
        .prefetch_related('posts')
        .prefetch_related('comments')
    )


class EditProfileView(UpdateView):
    model = get_user_model()
    template_name = 'users/edit_profile.html'
    form_class = EditProfileForm

    def get_context_data(self, **context):
        context['form'] = EditProfileForm(instance=self.object)
        return super().get_context_data(**context)

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object() and not request.user.has_perm(
                'users.change_user'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
