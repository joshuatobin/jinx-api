from django.test import TestCase
import ConfigParser
import clusto
import llclusto
import jinx_json



class JinxTestCase(TestCase):
    """A helper base class to make designing tests for API calls easier"""
    
    # Subclasses should override this with the full URL path to the call
    # they're testing.
    #
    # Example: /jinx/2.0/get_hosts_in_rack
    
    api_call_path = None
    
    def setUp(self):
        # Mostly cribbed from clusto's test framework
        
        conf = ConfigParser.ConfigParser()
        conf.add_section('clusto')
        conf.set('clusto', 'dsn', 'sqlite:///:memory:')
        clusto.connect(conf)
        clusto.init_clusto()
        clusto.clear()
        clusto.SESSION.close()
        clusto.init_clusto()
        self.data()
        
    def tearDown(self):
        if clusto.SESSION.is_active:
            raise Exception("SESSION IS STILL ACTIVE in %s" % str(self.__class__))
        
        clusto.clear()
        clusto.disconnect()
        clusto.METADATA.drop_all(clusto.SESSION.bind)
        
        
    def data(self):
        pass
        
    def do_api_call(self, *args):
        """Performs the API call for this test case and returns the results.
        
        JSON encoding and decoding is handled behind the scenes.  The decoded
        response data is stored in response.data (as opposed to 
        response.content, which will hold the raw JSON blob).
        """
        
        response = self.client.post(self.api_call_path, jinx_json.dumps(list(args)), "application/json")
        
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], "application/json", 
                "API call %s(%s) returned type %s instead of application/json" % (self.api_call_path, str(args), response['Content-Type']))
                
            response.data = jinx_json.loads(response.content)
        else:
            response.data = response.content
        
        return response
    
    def assert_response_code(self, response, code, description=None):
        self.assertEqual(response.status_code, code, description)
