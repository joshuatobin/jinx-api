from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import Class5Server, ServerClass, LindenDatacenter, LindenRack, Class7Server, Class7Chassis
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

        dfw = LindenDatacenter("DFW", "1234 Anywhere", "123 Anywhere street", "remotehands@remote.com")
        phx = LindenDatacenter("PHX", "1234 Anywhere", "123 Anywhere street", "remotehands@remote.com")

        rack1 = LindenRack("c1.01.1000")
        rack2 = LindenRack("c3.03.2000")

        dfw.insert(rack1)
        phx.insert(rack2)

        ServerClass("Class 7")
        chassis = Class7Chassis()
        rack1.insert(chassis, [1, 2])
        class7 = Class7Server("hostname2.lindenlab.com")
        class7.serial_number = "SM55880"
        class7.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:96")
        class7.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:97")

        chassis.insert(class7)
        
        rack2.insert(h1, 1)


    def test_normal_call(self):
        response = self.do_api_call("hostname1.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': [1], 
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'colo': 'PHX',
                                         'rack': "c3.03.2000"})

        response = self.do_api_call("aa:bb:cc:11:22:33")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': [1],
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'colo': 'PHX',
                                         'rack': "c3.03.2000"})

        response = self.do_api_call("aa:bb:cc:11:22:34")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': [1],
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'colo': 'PHX',
                                         'rack': "c3.03.2000"})

        response = self.do_api_call("hostname2.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:96', 'aa:bb:cc:11:22:97'],
                                         'positions': [1, 2],
                                         'hostname': 'hostname2.lindenlab.com',
                                         'pdu_connections': [],
                                         'serial_number': 'SM55880',
                                         'colo': 'DFW',
                                         'rack': "c1.01.1000"})

    def test_bad_call(self):
        response = self.do_api_call("huh?")
        self.assert_response_code(response, 404)
        
        response = self.do_api_call("huh?", 2)
        self.assert_response_code(response, 400)
