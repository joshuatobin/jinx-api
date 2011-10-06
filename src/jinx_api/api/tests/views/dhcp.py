from api.tests.base import JinxTestCase
import clusto
import llclusto
from llclusto.drivers import Class5Server, Class7Server, ServerClass, HostState
import sys


class TestSetDhcpAssociation(JinxTestCase):
    api_call_path = "/jinx/2.0/set_dhcp_association"

    def data(self):
        class5 = ServerClass("Class 5", num_cpus=1, cores_per_cpu=2, ram_size=3, disk_size=4)
        class7 = ServerClass("Class 7", num_cpus=2, cores_per_cpu=4, ram_size=6, disk_size=8)
        HostState("up")

        # Instantiate an entity without a hostname
        self.h1 = Class5Server()
        self.h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        self.h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")
        
        self.h2 = Class7Server()
        self.h2.set_ipmi_info("mgmt.foo", "aa:bb:cc:11:22:35")

    def test_normal_call(self):
        response = self.do_api_call("sim8000.agni.lindenlab.com", "aa:bb:cc:11:22:33")
        self.assert_response_code(response, 200)

        host = llclusto.get_by_hostname("sim8000.agni.lindenlab.com")[0]
        self.assertEquals(host, self.h1)

        mac = host.get_port_attr('nic-eth', 1, 'mac')
        self.assertEquals(mac, "aa:bb:cc:11:22:33")

        # Set a hostname on nic-eth 2.
        response = self.do_api_call("sim4000.agni.lindenlab.com", "aa:bb:cc:11:22:34")
        self.assert_response_code(response, 200)

        host = llclusto.get_by_hostname("sim4000.agni.lindenlab.com")[0]
        mac = host.get_port_attr('nic-eth', 2, 'mac')
        self.assertEquals(host, self.h1)
        self.assertEquals(mac, "aa:bb:cc:11:22:34")
        
        # Set IPMI hostname.
        response = self.do_api_call("mgmt.sim8000.agni.lindenlab.com", "aa:bb:cc:11:22:35")
        self.assert_response_code(response, 200)
        
        self.assertEquals(self.h2.ipmi, ('mgmt.sim8000.agni.lindenlab.com', "aa:bb:cc:11:22:35"))

class TestDeleteDhcpAssociation(JinxTestCase):
    api_call_path = "/jinx/2.0/delete_dhcp_association"

    def data(self):
        class5 = ServerClass("Class 5", num_cpus=1, cores_per_cpu=2, ram_size=3, disk_size=4)
        HostState("up")

        h1 = Class5Server("sim8000.agni.lindenlab.com")
        h1.set_port_attr("nic-eth", 1, "mac", "aa:bb:cc:11:22:33")
        h1.set_port_attr("nic-eth", 2, "mac", "aa:bb:cc:11:22:34")


    def test_normal_call(self):
        response = self.do_api_call("sim8000.agni.lindenlab.com", "aa:bb:cc:11:22:33")
        self.assert_response_code(response, 200)

        host = clusto.get_by_mac("aa:bb:cc:11:22:33")[0]
        self.assertEquals(host.hostname, None)

        # Test a bogus call
        response = self.do_api_call("sim2000.agni.lindenlab.com", "aa:bb:cc:11:00:99")
        self.assert_response_code(response, 409)

