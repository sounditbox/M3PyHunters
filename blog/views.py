from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# FBV - Function Based View
def my_first_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'first_view.html')
