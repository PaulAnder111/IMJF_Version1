from django.db import connections
from django.db.utils import OperationalError
from django.shortcuts import render

class DatabaseCheckMiddleware:
    """
    Middleware pou verifye si DB a disponib.
    Si li tonbe, montre paj db_error.html.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Tcheke baz done default la
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            return render(request, 'db_error.html', status=503)

        response = self.get_response(request)
        return response
