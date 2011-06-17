from django.test import TestCase
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.conf.urls.defaults import patterns, include
import jinx_json
import views
import datetime

# First, define a urlconf and some views that will be used to test only the
# API middleware, not the real Jinx API call functions.

urlpatterns = patterns('api.tests.api_tests',
    (r'test_view_normal', 'test_view_normal'),
    (r'test_view_exception', 'test_view_exception'),
    (r'test_view_not_found', 'test_view_not_found_response'),
    (r'test_view_echo', 'test_view_echo'),
    (r'test_view_reverse_three_arguments', 'test_view_reverse_three_arguments'),
    (r'test_view_one_default_argument', 'test_view_one_default_argument'),
    (r'test_doc', 'test_doc'),
)


def test_view_normal(request):
    """Simply return a string to mimic a normally functioning view."""
    
    return "Hello, world!"
    
def test_view_exception(request):
    """Raise an exception to mimic a view with a bug."""
    
    # Raises AttributeError
    None.foo

def test_view_not_found_response(request):
    """Return a 404 response to mimic requesting data that doesn't exist from an API call."""
    
    return HttpResponseNotFound("Not found.")

def test_view_echo(request, *args):
    """Return a list with exactly the arguments sent to facillitate testing JSON layer."""
    
    return args
    
def test_view_reverse_three_arguments(request, arg1, arg2, arg3):
    """Return a list with the three arguments in reverse order, to facillitate testing argument passing."""
    
    return [arg3, arg2, arg1]
    
def test_view_one_default_argument(request, arg="default"):
    """Return the argument passed to facillitate testing arguments with defaults."""
    
    return arg
    
def test_doc(request, arg1, arg2=3):
    """Test fetching of documentation strings.
    
    Note: This documentation string is used as part of the test.
    
        Please do not alter its formatting or parameter list.
    """
    
    pass
    

# Django's default 404 and 500 handlers want templates, 404.html and 500.html.
# I define new handlers here that don't care about templates.
    
def handler404(request):
    return HttpResponseNotFound("Not Found")

def handler500(request):
    return HttpResponseServerError("Server Error")


# And now the test suite:

class JinxAPITests(TestCase):
    """Test the Jinx API structure itself.  
    
    This tests everything in the middleware but nothing inside the API calls.
    Tested functionality includes:
    
    * JSON request/response
    * argument passing
    * exception handling
    """

    # Use the 'urls' functionality from Django's TestCase class to add a few 
    # views that help me test the middleware:
    urls = 'api.tests'
    
    def _post_json(self, path, data):
        """Perform a JSON-based post using the Django test client.
        
        The supplied data will be converted to JSON.  The response will be
        returned verbatim, without being converted from JSON format.
        """
        
        return self.client.post(path, jinx_json.dumps(data), "application/json")
    
    def _assert_api_status_code(self, response, code, description):
        self.assertTrue('X-Jinx-Error-Source' not in response or response['X-Jinx-Error-Source'] != 'api',
            description + " (expected a status code from the API structure, but got %d the API call)" % response.status_code)
        
        self.assertEqual(response.status_code, code, description)
    
    def test_invalid_call(self):
        response = self.client.get('/test_view_normal')
        self._assert_api_status_code(response, 405, 
            "A GET request should result in HTTP 405 Method Not Allowed.")
            
        response = self.client.post('/test_view_normal')
        self._assert_api_status_code(response, 415,
            "A POST with a Content-Type other than application/json should result in HTTP 415 Unsupported Media Type.")
        
        response = self.client.post('/test_view_normal', "This is not valid JSON data.", "application/json")
        self._assert_api_status_code(response, 415,
            "A POST with invalid JSON data should result in HTTP 415 Unsupported Media Type.")
            
        response = self._post_json('/test_view_normal', 2)
        self._assert_api_status_code(response, 400,
            "A POST with JSON data that is not a list should result in HTTP 400 Bad Request.")

    def test_normal_call(self):
        response = self._post_json("/test_view_normal", [])
        
        self.assertEqual(jinx_json.loads(response.content), "Hello, world!", 
            'test_view_normal should return "Hello, world!"')
        self._assert_api_status_code(response, 200,
            'test_view_normal should return status code 200.')


    def _assert_call_status_code(self, response, code, description):
        self.assertTrue('X-Jinx-Error-Source' in response and response['X-Jinx-Error-Source'] == 'api',
            description + " (expected a status code from the API call, but got %d from the API structure)" % response.status_code)
        
        self.assertEqual(response.status_code, code, description)
    
    def test_call_exception(self):
        response = self._post_json('/test_view_exception', [])
        self._assert_call_status_code(response, 500, 'Should get HTTP 500 when view throws an unhandled exception')
    
    def test_call_404(self):
        response = self._post_json('/test_view_not_found_response', [])
        self._assert_call_status_code(response, 404, 
            'Should get HTTP 404 with "X-Jinx-Error-Source: api" when view returns HttpResponseNotFound')
    
    def test_nonexistent_call(self):
        response = self._post_json('/nonexistentcallblahblah', [])
        self._assert_api_status_code(response, 404,
            'Should get an HTTP 404 with no "X-Jinx-Error-Source: api" header when making nonexistent API call')
    
    def test_arguments(self):
        response = self._post_json('/test_view_reverse_three_arguments', [1,2,"3"])
        self._assert_api_status_code(response, 200, "/test_view_reverse_three_arguments should return HTTP 200.")
        self.assertEqual(jinx_json.loads(response.content), ["3", 2, 1], 
            "/test_view_reverse_three_arguments should return the three arguments in reverse order.")
        
        response = self._post_json('/test_view_echo', [1])
        self._assert_api_status_code(response, 200, '/test_view_echo should return HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), [1], "/test_view_echo([1]) should return [1]")
        
        response = self._post_json('/test_view_echo', [1,2,3])
        self._assert_api_status_code(response, 200, '/test_view_echo should return HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), [1,2,3], 
            "/test_view_echo([1]) should return [1,2,3] (variable number of arguments should work)")
        
        response = self._post_json('/test_view_reverse_three_arguments', [1, 2])
        self._assert_call_status_code(response, 400, 
            '/test_view_reverse_three_arguments with 2 arguments should result in HTTP 400.')
            
        response = self._post_json('/test_view_reverse_three_arguments', [1, 2, 3, 4])
        self._assert_call_status_code(response, 400, 
            '/test_view_reverse_three_arguments with 4 arguments should result in HTTP 400.')
        
        response = self._post_json('/test_view_one_default_argument', ["testarg"])
        self._assert_api_status_code(response, 200, 
            '/test_view_one_default_argument with 1 argument should result in HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), "testarg")
        
        response = self._post_json('/test_view_one_default_argument', [])
        self._assert_api_status_code(response, 200, 
            '/test_view_one_default_argument with no arguments should result in HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), "default",
            '/test_view_one_default_argument should return "default" if no argument is passed.')
        
        response = self._post_json('/test_view_one_default_argument', [1, 2])
        self._assert_call_status_code(response, 400, 
            '/test_view_one_default_argument with 2 arguments should result in HTTP 400.')
    
    def test_datetime(self):
        now = datetime.datetime.now()
        response = self._post_json('/test_view_echo', [now])
        self._assert_api_status_code(response, 200, '/test_view_echo should return HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), [now],
            "should be able to send and receive datetime.datetime objects")
            
        delta = datetime.timedelta(seconds=1394875, days=21)
        response = self._post_json('/test_view_echo', [delta])
        self._assert_api_status_code(response, 200, '/test_view_echo should return HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), [delta],
            "should be able to send and receive datetime.timedelta objects")
        
        response = self._post_json('/test_view_echo', [[[[[[{'1': now}]]], {'2': delta}]]])
        self._assert_api_status_code(response, 200, '/test_view_echo should return HTTP 200.')
        self.assertEqual(jinx_json.loads(response.content), [[[[[[{'1': now}]]], {'2': delta}]]],
            "should be able to send and receive datetime.datetime and datetime.timedelta inside complex data structures")

    
    def test_doc(self):
        expected_documentation = \
"""test_doc(arg1, arg2=3):
Test fetching of documentation strings.

Note: This documentation string is used as part of the test.

    Please do not alter its formatting or parameter list."""
    
        response = self.client.get('/test_doc?doc')
        self.assertEquals(response.status_code, 200, "GET request for documentation should result in HTTP 200 (got %d)." % response.status_code)
        self.assertEquals(response.content, expected_documentation,
            "Documentation did not match expected value... perhaps whitespace was not stripped properly?")
        
        response = self._post_json('/test_doc?doc', [1])
        self.assertEquals(response.status_code, 200, "POST request for documentation should also result in HTTP 200.")
        self.assertEquals(response.content, expected_documentation,
            "Documentation did not match expected value... perhaps whitespace was not stripped properly?")
        

    
