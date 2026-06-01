from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


# FBV - Function Based View
def my_first_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'first_view.html')


def dynamic_view(request: HttpRequest, conv: str) -> HttpResponse:
    # запрос к бд - вытащить отдельную статью
    # сформировать контекст для html
    return HttpResponse(f'<h1>Counter {conv}</h1>')


def two_vars(request: HttpRequest, var1: int, var2: int) -> HttpResponse:
    return HttpResponse(f'<h1>Data from url: 1:{var1}, 2:{var2}</h1>')


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


def get_post(request: HttpRequest, post_id: int) -> HttpResponse:
    if post_id not in pseudo_db['posts']:
        return HttpResponse('<h1 style="color: red;">Post not found</h1>')
    post = pseudo_db['posts'][post_id]

    response = f'<br><a href="{reverse('blog:post_list')}">'
    response += '<button>Back to posts</button></a>'

    response += f'<h1>{post["title"]}</h1><p>{post["content"]}</p><br>'
    response += (f'<a href="{reverse('blog:comments', args=[post_id])}">'
                 '<button>Comments</button></a>')

    return HttpResponse(response)


def get_post_comments(request, post_id):
    if post_id not in pseudo_db['posts']:
        return HttpResponse('<h1 style="color: red;">Post not found</h1>')
    # comments = list(filter(lambda c: c['post_id'] == post_id, pseudo_db['comments'].values()))
    comments = [c for c in pseudo_db['comments'].values() if
                c['post_id'] == post_id]

    response = f'<a href="{reverse('blog:post_detail', args=[post_id])}">'
    response += '<button>Back to post</button></a>'

    response += f'<h1>Comments for post {post_id}</h1>'
    for c in comments:
        response += f'<p>{c["content"]}</p>'

    return HttpResponse(response)


def post_list(request: HttpRequest) -> HttpResponse:
    posts = [p for p in pseudo_db['posts'].values()]
    response = '<h1>All Posts</h1>'
    for p in posts:
        response += (f'<a href="{reverse('blog:post_detail', args=[p['id']])}">'
                     f'<h2>{p["title"]}</h2>'
                     f'</a>')
    response = HttpResponse(response)
    response['My-Custom-Header'] = 'Custom Value'
    response.status_code = 418
    return response


@csrf_exempt
def request_review(request: HttpRequest) -> HttpResponse:
    response = '<h1>Request Data:</h1>'
    response += f'<p>Method: {request.method}</p>'
    response += f'<p>Path: {request.path}</p>'

    # response += f'<h2>Headers:</h2>'
    # response += f'{request.headers}</p>'
    #
    # response += f'<h2>Body:</h2>'
    # response += f'<p>{request.body}</p>'

    # response += f'<h2>Cookies:</h2>'
    # response += f'<p>{request.COOKIES}</p>'

    # Параметры из url
    response += '<h2>Query Params:</h2>'
    for p in request.GET:
        response += f'<p>{p}: {request.GET[p]}</p>'

    # Данные из формы
    if request.POST:
        response += f'<h2>Post data:</h2>'
        for p in request.POST:
            response += f'<p>{p}: {request.POST[p]}</p>'

    # Если в форме присылался файл
    if request.FILES:
        response += f'<h2>Files attached:</h2>'

        for f in request.FILES:
            response += f'<p>{f}: {request.FILES[f].read()}</p>'

        with open('file.jpg', 'wb') as f:
            f.write(request.FILES['file'].read())

    if request.user.is_authenticated:
        response += f'<h2>User: {request.user}'
    else:
        response += f'<h2>Not logged in</h2>'

    return HttpResponse(response)
