import datetime

from config import settings


def current_year(request):
    return {'current_year': datetime.datetime.now().year}


def site_name(request):
    return {'site_name': settings.SITE_NAME}
