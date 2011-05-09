import simplejson
from django.http import HttpResponse, HttpResponseBadRequest
import functools

def handle_json(view):
    """A decorator for processing JSON requests and encoding JSON responses.
    
    Clients will send requests with content type of application/json.  The
    JSON data will be a list of arguments for to the API call.  The API call
    will respond with an arbitrary piece of JSON-able data, which this 
    decorator will then encode as an application/json response body.
    
    This decorator will unpack the list of arguments and pass them in to the
    decorated function.
    """
    
    def decorated_view(request):
        content_type = request.META['CONTENT_TYPE']
        method = request.META['REQUEST_METHOD']
        
        if method != 'POST' or content_type != "application/json":
            return HttpResponseBadRequest('The Jinx API requires POSTs with Content-Type: application/json')
            
        json_data = request.raw_post_data
        
        args = simplejson.loads(json_data)
        
        if type(args) != list:
            return HttpResponseBadRequest('Expected a list of arguments; got ' % str(type(args))
            
        try:
            response_data = view(request, *args)
        except TypeError, e:
            # This will return an HTTP 401 with a body like this:
            #   the_function_name() tatkes 4 arguments (3 given)
            return HttpResponseBadRequest(str(e))
        
        try:
            response_json = simplejson.dumps(response_data)
        except TypeError, e:
            return HttpResponseServerError('%s returned unserializable data: %s' % (view.__name__, str(e)))
            
        return HttpResponse(response_json, mimetype='application/json')
        
    # This sets decoreated_view's __name__, __module__, and __doc__ to match 
    # the view function's, which makes debugging easier.
    functools.update_wrapper(decorated_view, view)
    
    return decorated_view
    
def check_authorization(view):
    """A decorator to check whether the client is authorized to access this
    view.
    
    Stubbed for now; we're asserting that anyone that can pass kerberos 
    authentication can access all API calls.  In the future, we'll use
    LDAP groups to limit access to API calls based on the kerberos principal.
    If LDAP says they're not authorized, return a 403 Forbidden.  We won't
    return a 401 Unauthorized, because that tells the client to try again.
    """
    
    def decorated_view(*args, **kwargs):
        """ For now, do the decorator equivalent of a no-op.
        """
        
        return view(*args, **kwargs)
        
    functools.update_wrapper(decorated_view, view)
    
    return decorated_view
    
    
