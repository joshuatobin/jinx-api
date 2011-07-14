from api.tests.base import JinxTestCase
import clusto
import llclusto
from llclusto.drivers import Class5Server, ServerClass, LindenDatacenter, LindenRack, HostState, LindenPDU, LindenSwitch
import sys

class TestJinxQueryRack(JinxTestCase):
    api_call_path = "/jinx/2.0/jinx_query_rack"

    def data(self):
        # Populate Clusto                                                                                                       
        ServerClass("Class 5")
        HostState("up")
        h1 = Class5Server("hostname1.lindenlab.com")
        h1.serial_number = "SM55880"
        h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")

        dfw = LindenDatacenter("DFW", "1234 Anywhere", "123 Anywhere street", "remotehands@remote.com")

        rack1 = LindenRack("c1.01.1000")
        dfw.insert(rack1)

        pdu = LindenPDU()
        pdu.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:12")
        rack1.attach_pdu(pdu)


        switch1 = LindenSwitch()
        switch1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:99")

        rack1.insert(switch1, 2)
        rack1.insert(h1, 1)

    def test_normal_call(self):
        response = self.do_api_call("c1.01.1000")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted([{'macs': ['aa:bb:cc:11:22:99'],
                                                         'positions': [2],
                                                         'hostname': None,
                                                         'pdu_connections': [],
                                                         'colo': 'DFW',
                                                         'serial_number': None,
                                                         'type': "switch",
                                                         'rack': "c1.01.1000"},
                                                        {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                                         'positions': [1],
                                                         'hostname': 'hostname1.lindenlab.com',
                                                         'pdu_connections': [],
                                                         'colo': 'DFW',
                                                         'serial_number': 'SM55880',
                                                         'type': "server",
                                                         'rack': "c1.01.1000"},
                                                        {'macs': ['aa:bb:cc:11:22:12'],
                                                         'positions': [],
                                                         'hostname': None,
                                                         'pdu_connections': [],
                                                         'colo': 'DFW',
                                                         'serial_number': None,
                                                         'type': "pdu",
                                                         'rack': "c1.01.1000"}]))


class TestJinxQueryHostnameMac(JinxTestCase):
    api_call_path = "/jinx/2.0/jinx_query_hostname_mac"

    def data(self):
        # Populate Clusto                                                                                                       
        ServerClass("Class 5")
        HostState("up")
        h1 = Class5Server("hostname1.lindenlab.com")
        h1.serial_number = "SM55880"
        h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")

        dfw = LindenDatacenter("DFW", "1234 Anywhere", "123 Anywhere street", "remotehands@remote.com")

        rack1 = LindenRack("c1.01.1000")
        dfw.insert(rack1)

        pdu = LindenPDU()
        pdu.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:12")
        pdu.hostname = "pdu1.lindenlab.com"
        pdu.connect_ports("pwr-nema-5",1,h1,1)

        rack1.attach_pdu(pdu)
        rack1.insert(h1, 1)

    def test_normal_call(self):
        response = self.do_api_call("aa:bb:cc:11:22:33")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': [1],
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [{'pdu': u'pdu1.lindenlab.com', u'port': 1}],
                                         'colo': 'DFW',
                                         'serial_number': 'SM55880',
                                         'type': "server",
                                         'rack': "c1.01.1000"})


        response = self.do_api_call("hostname1.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                         'positions': [1],
                                         'hostname': 'hostname1.lindenlab.com',
                                         'pdu_connections': [{'pdu': u'pdu1.lindenlab.com', u'port': 1}],
                                         'colo': 'DFW',
                                         'serial_number': 'SM55880',
                                         'type': "server",
                                         'rack': "c1.01.1000"})


class TestJinxQuerySerial(JinxTestCase):
    api_call_path = "/jinx/2.0/jinx_query_serial"

    def data(self):
        # Populate Clusto                                                                                                       
        ServerClass("Class 5")
        HostState("up")
        h1 = Class5Server("hostname1.lindenlab.com")
        h1.serial_number = "SM55880"
        h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")

        dfw = LindenDatacenter("DFW", "1234 Anywhere", "123 Anywhere street", "remotehands@remote.com")

        rack1 = LindenRack("c1.01.1000")
        dfw.insert(rack1)

        pdu = LindenPDU()
        pdu.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:12")
        rack1.attach_pdu(pdu)


        switch1 = LindenSwitch()
        switch1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:99")

        rack1.insert(switch1, 2)
        rack1.insert(h1, 1)

    def test_normal_call(self):
        response = self.do_api_call("SM55880")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted({'macs': ['aa:bb:cc:11:22:33', 'aa:bb:cc:11:22:34'],
                                                         'positions': [1],
                                                         'hostname': 'hostname1.lindenlab.com',
                                                         'pdu_connections': [{'pdu': u'pdu1.lindenlab.com', u'port': 1}],
                                                         'colo': 'DFW',
                                                         'serial_number': 'SM55880',
                                                         'type': "server",
                                                         'rack': "c1.01.1000"}))
