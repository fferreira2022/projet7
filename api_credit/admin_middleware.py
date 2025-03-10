from django.http import HttpResponseRedirect

class AdminMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path == '/admin/' or request.path.startswith('/admin/'):
            if not request.user.is_authenticated or not request.user.is_staff:
                return HttpResponseRedirect('/login/')
