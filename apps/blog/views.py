from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

pseudo_db = {
    'posts': {
        1: {'id': 1, 'title': 'Post 1', 'content': 'Content 1'},
        2: {'id': 2, 'title': 'Post 2', 'content': 'Content 2'},
        3: {'id': 3, 'title': 'New Post', 'content': 'New Content'},
    },
    'comments': {
        1: {'post_id': 1, 'content': 'Comment 1'},
        3: {'post_id': 1, 'content': 'Another comment'},
        2: {'post_id': 2, 'content': 'Comment 2'},
    }
}


# def get_post(request: HttpRequest, post_id: int) -> HttpResponse:
#     if post_id not in pseudo_db['posts']:
#         return render(request, '404.html', {'instance': f'Post {post_id}'})
#     post = pseudo_db['posts'][post_id]
#
#     context = {
#         'post': post,
#         'title': f'Post {post["title"]}'
#     }
#     return render(request, 'post_detail.html', context)


class PostDetailView(View):
    def get(self, request, post_id):
        if post_id not in pseudo_db['posts']:
            return render(request, '404.html', {'instance': f'Post {post_id}'})
        post = pseudo_db['posts'][post_id]

        context = {
            'post': post,
            'title': f'Post {post["title"]}'
        }
        return render(request, 'post_detail.html', context)



# def get_post_comments(request, post_id):
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         new_comment = {'post_id': post_id, 'content': content}
#         pseudo_db['comments'][len(pseudo_db['comments']) + 1] = new_comment
#         return redirect('blog:comments', post_id=post_id)
#
#     if post_id not in pseudo_db['posts']:
#         return render(request, '404.html', {'instance': f'Post {post_id}'})
#     comments = [c for c in pseudo_db['comments'].values() if
#                 c['post_id'] == post_id]
#     context = {
#         'comments': comments,
#         'post_id': post_id,
#         'title': f'Comments for post {post_id}'
#     }
#
#     return render(request, 'comment_list.html', context)


class CommentListView(View):
    def get(self, request, post_id):
        if post_id not in pseudo_db['posts']:
            return render(request, '404.html', {'instance': f'Post {post_id}'})
        comments = [c for c in pseudo_db['comments'].values() if
                    c['post_id'] == post_id]
        context = {
            'comments': comments,
            'post_id': post_id,
            'title': f'Comments for post {post_id}'
        }

        return render(request, 'comment_list.html', context)

    def post(self, request, post_id):
        content = request.POST.get('content')
        new_comment = {'post_id': post_id, 'content': content}
        pseudo_db['comments'][len(pseudo_db['comments']) + 1] = new_comment
        return self.get(request, post_id)


# def post_list(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         content = request.POST.get('content')
#         new_post = {'id': len(pseudo_db['posts']) + 1, 'title': title,
#                     'content': content}
#         pseudo_db['posts'][new_post['id']] = new_post
#     posts = [p for p in pseudo_db['posts'].values()]
#     context: dict[str, Any] = {
#         'title': 'All posts',
#         'posts': posts,
#     }
#     return render(request, 'post_list.html', context)


class PostListView(View):
    def get(self, request: HttpRequest):
        posts = [p for p in pseudo_db['posts'].values()]
        context: dict[str, Any] = {
            'title': 'All posts',
            'posts': posts,
        }
        return render(self.request, 'post_list.html', context)

    def post(self, request):
        title = self.request.POST.get('title')
        content = self.request.POST.get('content')
        new_post = {'id': len(pseudo_db['posts']) + 1, 'title': title,
                    'content': content}
        pseudo_db['posts'][new_post['id']] = new_post
        return self.get(request)

#
# class PostListView(TemplateView):
#     template_name = 'post_list.html'
#     extra_context = {
#         'title': 'All posts',
#         'posts': [p for p in pseudo_db['posts'].values()]
#     }
#
#     def post(self, request):
#         title = self.request.POST.get('title')
#         content = self.request.POST.get('content')
#         new_post = {'id': len(pseudo_db['posts']) + 1, 'title': title, 'content': content}
#         pseudo_db['posts'][new_post['id']] = new_post
#         return redirect('blog:post_list')
