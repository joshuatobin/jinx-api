from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import Class5Server, ServerClass, LindenRack
import sys

class TestGetRackContents(JinxTestCase):
    api_call_path = "/jinx/2.0/get_rack_contents"

    def data(self):
        # Populate Clusto
        rack = LindenRack("c2-02-00")
        ServerClass("Class 5")
        h1 = Class5Server("hostname1.lindenlab.com")
        h2 = Class5Server("hostname2.lindenlab.com")
        rack.insert(h1, 1)
        rack.insert(h2, 2)

    def test_normal_call(self):
        response = self.do_api_call("c2-02-00")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, [{'serial_number': None, 
                                          'hostname': 'hostname1.lindenlab.com', 
                                          'type': 'server'}, 
                                         {'serial_number': None, 
                                          'hostname': 'hostname2.lindenlab.com', 
                                          'type': 'server'}])

    def test_bad_call(self):
        response = self.do_api_call("huh?")
        self.assert_response_code(response, 404)
        
        response = self.do_api_call("huh?", 2)
        self.assert_response_code(response, 400)
