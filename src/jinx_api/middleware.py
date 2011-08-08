import jinx_json
import clusto.scripthelpers
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from jinx_api.http import HttpResponseUnsupportedMediaType, HttpResponseInvalidState
from jinx_client.jinx_exceptions import *
import functools
import traceback
import sys
import inspect
import subprocess
import re


def trim_docstring(docstring):
    """ Trim a docstring.
    
    Follows the rules of PEP 257:
    
    Strip a uniform amount of indentation from the second and further lines 
    of the docstring, equal to the minimum indentation of all non-blank lines
    after the first line. Any indentation in the first line of the docstring 
    (i.e., up to the first newline) is insignificant and removed. Relative 
    indentation of later lines in the docstring is retained. Blank lines should
    be removed from the beginning and end of the docstring.
    
    This following code was taken directly from PEP 257.
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


class APIDocumentationMiddleware(object):
    """Service requests for documentation"""
    
    def process_view(self, request, view, view_args, view_kwargs):
        """Check for a request for documentation and satisfy it.
        
        Documentation requests look like normal API calls, except that they use
        GET and have the 'doc' query parameter."""
        
        if 'doc' in request.GET:
            # I want to print something like this:
            #    view_name(arg1, arg2, arg3=default3, ...):
            # 
            # I'll have to construct it using the inspect module.
            
            args, varargs, varkwargs, defaults = inspect.getargspec(view)
            
            # Strip off the first parameter, which is the request object
            args = args[1:]
            
            signature = view.__name__
            
            # Defaults are kind of hairy.  inspect fills the defaults list in with
            # the default values of the trailing arguments in the args list.
            
            if defaults is not None:
                # First, peel off the arguments without defaults
                arg_list = list(args[:-len(defaults)])
                
                # Now, peel off the rest and add their default value:
                for arg, default in zip(args[-len(defaults):], defaults):
                    arg_list.append("%s=%s" % (arg, default))
            else:
                arg_list = args
            
            # Add a "..." if this function takes variable arguments
            if varargs is not None:
                arg_list.append("...")
            
            # Finish it off by separating the arguments with commas:
            signature += "(%s):" % ", ".join(arg_list)
            
            docstring = trim_docstring(view.__doc__)
            
            return HttpResponse(signature + "\n" + docstring, mimetype='text/plain')
            

class JSONMiddleware(object):
    """Handle JSON requests and responses"""

    def process_view(self, request, view, view_args, view_kwargs):
        """Handle a JSON-based API call.
        
        This function is called when Django is about to call a view.  It will
        decode a POST body in JSON format, call the view, and encode the
        response in JSON format.
        
        The request should be a POST with a Content-Type of "application/json".
        The body of the request should be a JSON-encoded list of arguments to
        pass to the API call.  The arguments will be unpacked and passed in as
        positional and keyword arguments to the view function as described 
        below.  If the view function returns data, it will be JSON-encoded and
        sent back as a response with Content-Type "application/json".  If the 
        view function returns an HttpResponse object, this will be sent back 
        to the client as is.
        
        The request body can specify API calls in one of two ways, the old 
        style or the new style.  In the old style, only positional arguments
        may be passed, and the request body is simply a list of positional
        arguments.  In the new style, both positional and keyword arguments may
        be passed, and the request body is a dict with 'args' and 'kwargs' 
        entries.  
        
        Old style: ['arg1', 'arg2']
        New style: {
                    'args': ['arg1', 'arg2'],
                    'kwargs': {'arg3': 'value3, 'arg4': 'value4'}
                   }
        
        Arguments:
            request -- The HttpRequest object from Django.
            view -- The view function that Django is about to call.
            view_args -- The position arguments Django would pass to the view.
            view_kwargs -- The keyword arguments Django would pass to the view.
            
        Status Codes Returned:
            200 -- The request was completed successfully.
            405 -- A method other than POST was used.
            415 -- A request body type other than application/json was sent.
            500 -- The view function raised an unhandled exception, or returned
                unserializable data (see exception value for details).
            ?   -- View functions may return whatever HTTP status codes they
                deem appropriate.  See the documentation for each view function.
            
        """
        
        content_type = request.META['CONTENT_TYPE']
        method = request.META['REQUEST_METHOD']
        
        if method != 'POST':
            return HttpResponseNotAllowed('The Jinx API requires a POST')
            
        if content_type != "application/json":
            return HttpResponseUnsupportedMediaType('The Jinx API requires a request with Content-Type: application/json')
            
        json_data = request.raw_post_data
        
        try:
            json_args = jinx_json.loads(json_data)
        except ValueError, e:
            return HttpResponseUnsupportedMediaType('Request body could not be parsed as a JSON object: %s' % str(e))
        
        args = list(view_args)
        kwargs = view_kwargs
        
        if type(json_args) == list:
            args += json_args
        elif type(json_args) == dict:
            if sorted(json_args.keys()) != ['args', 'kwargs']:
                return HttpResponseBadRequest("Expected a dict with only 'args' and 'kwargs' keys; got %s" % str(json_args.keys()))
            else:
                args += json_args['args']
                kwargs.update(json_args['kwargs'])
        else:
            return HttpResponseBadRequest("Expected a list of arguments or a dict with 'args' and 'kwargs'; got %s" % str(type(json_args)))
        
        try:
            response_data = view(request, *args, **kwargs)
            if clusto.SESSION.is_active:
                raise Exception('SESSION IS STILL ACTIVE after running %s(%s, %s)' % (view.__name__, args, kwargs))
        except TypeError, e:
            # This will return an HTTP 400 with a body like this:
            #   the_function_name() takes 4 arguments (3 given)
            response_data = HttpResponseBadRequest(str(e))
        except JinxInvalidRequestError, e:
            response_data = HttpResponseBadRequest(str(e))
        except JinxActionForbiddenError, e:
            response_data = HttpResponseForbidden(str(e))
        except JinxDataNotFoundError, e:
            response_data = HttpResponseNotFound(str(e))
        except JinxInvalidStateError, e:
            response_data = HttpResponseInvalidState(str(e))
        except:
            exception_traceback = traceback.format_exception(*sys.exc_info())
            
            #print >> sys.stderr, "Unhandled exception from view:"
            #print >> sys.stderr, exception_traceback
            
            response_data = HttpResponseServerError(exception_traceback, mimetype='text/plain')
        
        # At this point, if response_data is an HttpResponse subclass, mark the
        # error as having come from the API call and send it back
        if isinstance(response_data, HttpResponse):
            response_data['X-Jinx-Error-Source'] = 'api'
            return response_data
        else:
            try:
                response_json = jinx_json.dumps(response_data)
            except TypeError, e:
                return HttpResponseServerError('%s returned unserializable data: %s' % (view.__name__, str(e)))
            
        return HttpResponse(response_json, mimetype='application/json')


class JinxAuthorizationMiddleware(object):
    def __init__(self):
        self.principal_re = re.compile(r'^(?P<user>[^/@]+)(/(?P<cluster>[^@]+))?@(?P<realm>.*)$')
    
    def get_cluster_name(self):
        try:
            return self.cluster_name
        except AttributeError:
            try:
                cluster_name = subprocess.Popen(["/usr/bin/get-conf-linden", "--cluster"], stdout=subprocess.PIPE).communicate()[0]
                cluster_name = cluster_name.strip()
            
                if cluster_name.startswith('cluster-name: '):
                    self.cluster_name = cluster_name[14:]
            except OSError:
                self.cluster_name = None
                
            return self.cluster_name
    
    def process_view(self, request, view, view_args, view_kwargs):
        """Return a 403 Forbidden status if LDAP says the user may not make this API call."""
        
        if not request.META.get('REMOTE_USER'):
            # I'd like to throw a 403 here but that'd break the unit tests.
            request.META['REMOTE_USER'] = None
            return
        
        krb_principal = request.META['REMOTE_USER']
        
        match = self.principal_re.match(krb_principal)
        
        if match:
            user = match.group('user')
            cluster = match.group('cluster')
            
            if cluster:
                if cluster != self.get_cluster_name():
                    return HttpResponseForbidden('%s may not access this server which is in the %s cluster' % (krb_principal, self.cluster_name))
            
            # Do authorization checks here...
            request.META['REMOTE_USER'] = user
            
        return

