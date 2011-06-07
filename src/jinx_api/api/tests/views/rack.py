from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import Class5Server, Class7Server, Class7Chassis, ServerClass, LindenRack
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


class TestGetServerHostnamesInRack(JinxTestCase):
    api_call_path = "/jinx/2.0/get_server_hostnames_in_rack"
    
    def data(self):
        # Populate Clusto                                                                                                                                            
        ServerClass("Class 5")
        h1 = Class5Server("hostname1.lindenlab.com")
        h2 = Class5Server("hostname2.lindenlab.com")

        rack1 = LindenRack("c3-03-100")
        rack2 = LindenRack("c3-03-200")

        ServerClass("Class 7")

        chassis1 = Class7Chassis()
        chassis2 = Class7Chassis()

        class7_1 = Class7Server("hostname3.lindenlab.com")
        class7_2 = Class7Server("hostname4.lindenlab.com")
        
        chassis1.insert(class7_1)
        chassis2.insert(class7_2)

        rack2.insert(h1, 1)

        rack1.insert(chassis1, [1, 2])
        rack1.insert(chassis2, [3, 4])
        rack1.insert(h2, 5)

    def test_normal_call(self):
        response = self.do_api_call("c3-03-100")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), ['hostname2.lindenlab.com', 'hostname3.lindenlab.com', 'hostname4.lindenlab.com'])

        response = self.do_api_call("c3-03-200")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), ['hostname1.lindenlab.com']

