from api.tests.base import JinxTestCase
import clusto
import llclusto
from llclusto.drivers import Class5Server, ServerClass, LindenDatacenter, LindenRack, Class7Server, Class7Chassis, HostState
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
        
class TestGetHostState(JinxTestCase):
    api_call_path = "/jinx/2.0/get_host_state"
    
    def data(self):
        ServerClass("Class 5")
        server1 = Class5Server("test1.lindenlab.com")
        server2 = Class5Server("test2.lindenlab.com")
        HostState("up")
        server1.state = "up"
        
    def test_get_host_state(self):
        response = self.do_api_call("test1.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "up")
    
    def test_no_state(self):
        response = self.do_api_call("test2.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
    
    def test_nonexistent_host(self):
        response = self.do_api_call("test3.lindenlab.com")
        self.assert_response_code(response, 404)
        
class TestSetHostState(JinxTestCase):
    api_call_path = "/jinx/2.0/set_host_state"
    
    def data(self):
        ServerClass("Class 5")
        self.server1 = Class5Server("test1.lindenlab.com")
        HostState("up")
        HostState("down")

    def test_set_host_state(self):
        response = self.do_api_call("test1.lindenlab.com", "up")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.server1.state, "up")
        
        state_up = clusto.get_by_name("up")
        self.assertTrue(self.server1 in state_up)
        
        response = self.do_api_call("test1.lindenlab.com", "down")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.server1.state, "down")
        
        state_down = clusto.get_by_name("down")
        
        self.assertTrue(self.server1 not in state_up)
        self.assertTrue(self.server1 in state_down)
    
    def test_nonexistent_host(self):
        response = self.do_api_call("test3.lindenlab.com", "up")
        self.assert_response_code(response, 404)

    def test_nonexistent_host(self):
        response = self.do_api_call("test1.lindenlab.com", "sideways")
        
        self.assert_response_code(response, 409)
        
    def test_delete_state(self):
        self.server1.state = "up"
    
        response = self.do_api_call("test1.lindenlab.com", None)
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, None)
        self.assertEqual(self.server1.state, None)

class TestGetHostsInState(JinxTestCase):
    api_call_path = "/jinx/2.0/get_hosts_in_state"
    
    def data(self):
        ServerClass("Class 5")
        self.server1 = Class5Server("test1.lindenlab.com")
        self.server2 = Class5Server("test2.lindenlab.com")
        HostState("up")
        HostState("down")
    
    def test_get_hosts_in_state(self):
        response = self.do_api_call("up")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, [])
        
        self.server1.state = "up"
        
        response = self.do_api_call("up")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, [self.server1.hostname])
        
        self.server2.state = "up"
        
        response = self.do_api_call("up")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(sorted(response.data), sorted([self.server1.hostname, self.server2.hostname]))
        
        self.server2.state = "down"
        
        response = self.do_api_call("up")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, [self.server1.hostname])
        
        response = self.do_api_call("down")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, [self.server2.hostname])
        
    def test_nonexistent_state(self):
        response = self.do_api_call("sideways")
        self.assert_response_code(response, 409, response.data)

class TestListHostStates(JinxTestCase):
    api_call_path = "/jinx/2.0/list_host_states"
    
    def test_list_host_states(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, [])
        
        HostState("up")
        
        response = self.do_api_call()
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, ["up"])
        
        HostState("down")
        
        response = self.do_api_call()
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(sorted(response.data), ["down", "up"])

class TestAddHostState(JinxTestCase):
    api_call_path = "/jinx/2.0/add_host_state"
    
    def test_add_host_state(self):
        response = self.do_api_call("up")
        self.assert_response_code(response, 200, response.data)
        self.assertEqual(response.data, None)
        
        try:
            up = clusto.get_by_name("up")
        except LookupError:
            self.fail("host state 'up' was not added")
        
        self.assertEqual(up.name, "up")
        self.assertTrue(isinstance(up, HostState))
    
    def test_add_existing_state(self):
        HostState("up")
        response = self.do_api_call("up")
        self.assert_response_code(response, 409, response.data)
    
    def test_add_invalid_state(self):
        response = self.do_api_call("?(*&@5")
        self.assert_response_code(response, 400, response.data)


