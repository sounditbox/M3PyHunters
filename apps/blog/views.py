from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, \
    DeleteView, FormView, TemplateView

from apps.blog.forms import PostCreateForm, FeedbackForm, CommentCreateForm
from apps.blog.mixins import MessagesOnFormProcessingMixin, \
    SuccessMessageOnFormValidMixin
from apps.blog.models import Post, Comment


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_data'] = Comment.objects.aggregate(
            total_comments=Count('id'))
        return context

    def get(self, request, **kwargs):
        self.object = self.get_object()
        self.object.views = F('views') + 1
        self.object.save()
        return super().get(request, **kwargs)


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    extra_context = {'title': 'All Posts'}
    ordering = ['created_at']
    # queryset = (Post.objects.filter(
    #     Q(status='published') & (~Q(likes__lt=10) | Q(views__gt=100)))
    #             .prefetch_related('comments').prefetch_related('tags')
    #             .annotate(total_comments=Count('comments__id'))
    #             )
    paginate_by = 10


class PostCreateView(MessagesOnFormProcessingMixin, LoginRequiredMixin,
                     CreateView):
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'create_post.html'
    success_message = 'Post created successfully'
    error_message = 'Failed to create post'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@login_required
def post_create(request):
    form = PostCreateForm()

    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('user_agreement')
            Post.objects.create(**form.cleaned_data)
            messages.success(request, 'Post created successfully',
                             extra_tags='alert alert-success')
            return redirect('blog:post_list')
        else:
            messages.error(request, 'Failed to create post',
                           extra_tags='alert alert-danger')
    return render(request, 'create_post.html', {'form': form})


class FeedbackView(SuccessMessageOnFormValidMixin, FormView):
    form_class = FeedbackForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'blog/feedback.html'
    success_message = 'Ваше сообщение успешно отправлено!'

    def form_valid(self, form):
        name, email, message = form.cleaned_data.values()
        print(f'{name} ({email}) написал: {message}')
        return super().form_valid(form)


class PostDeleteView(MessagesOnFormProcessingMixin, LoginRequiredMixin,
                     DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post_list')
    template_name = 'delete_post.html'
    pk_url_kwarg = 'post_id'
    success_message = 'Post deleted successfully'
    error_message = 'Failed to delete post'


class PostUpdateView(MessagesOnFormProcessingMixin, LoginRequiredMixin,
                     UpdateView):
    model = Post
    form_class = PostCreateForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'create_post.html'
    pk_url_kwarg = 'post_id'
    success_message = 'Post updated successfully'
    error_message = 'Failed to update post'


class CommentListView(MessagesOnFormProcessingMixin, CreateView):
    model = Comment
    context_object_name = 'comments'
    paginate_by = 10
    template_name = 'blog/comment_list.html'
    form_class = CommentCreateForm
    success_message = 'Comment created successfully'
    error_message = 'Failed to create comment'

    def get_success_url(self):
        return reverse_lazy('blog:comments',
                            kwargs={'post_id': self.kwargs['post_id']})

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def get_context_data(self, **context):
        context['comments'] = self.get_queryset()
        context['post_id'] = self.kwargs['post_id']
        return super().get_context_data(**context)

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['post_id']
        form.instance.author = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        return super().post(request, *args, **kwargs)
