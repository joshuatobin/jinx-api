from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import Class5Server, ServerClass
import sys

class TestGetHostsByRegex(JinxTestCase):
    api_call_path = "/jinx/2.0/get_hosts_by_regex"
    
    def data(self):
        # Populate Clusto
        ServerClass("Class 5")
        Class5Server("hostname1")
        Class5Server("hostname2")
        Class5Server("hostname3")
        Class5Server("hostname4")
        Class5Server("hostname5")
        Class5Server("anothername1")
    
    def test_normal_call(self):
        response = self.do_api_call(r'^hostname[3-9]')
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), ["hostname3", "hostname4", "hostname5"])
        
        response = self.do_api_call(r'nothername.*')
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), ["anothername1"])
        
    def test_bad_regex(self):
        response = self.do_api_call(r'^(badregex')
        self.assert_response_code(response, 400)


class TestGetRemoteHandsInfo(JinxTestCase):
    api_call_path = "/jinx/2.0/get_host_remote_hands_info"

    def data(self):
        # Populate Clusto
        ServerClass("Class 5")
        h1 = Class5Server("hostname1.lindenlab.com")
        h1.serial_number = "SM55880"
        h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")

    def test_normal_call(self):
        response = self.do_api_call("hostname1.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': None, 
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'rack': None})

        response = self.do_api_call("aa:bb:cc:11:22:33")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': None,
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'rack': None})

        response = self.do_api_call("aa:bb:cc:11:22:34")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': None,
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'rack': None})

    def test_bad_call(self):
        response = self.do_api_call("huh?")
        self.assert_response_code(response, 404)
        
        response = self.do_api_call("huh?", 2)
        self.assert_response_code(response, 400)
