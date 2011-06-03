"""Define subclasses of django.http.HttpResponse for status codes Django doesn't already provide classes for."""

from django.http import HttpResponse

class HttpResponseInvalidState(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs['status'] = 409
        
        super(HttpResponseInvalidState, self).__init__(*args, **kwargs)

class HttpResponseUnsupportedMediaType(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs['status'] = 415
        
        super(HttpResponseUnsupportedMediaType, self).__init__(*args, **kwargs)

