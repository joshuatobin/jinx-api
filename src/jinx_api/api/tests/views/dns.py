from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import DNSRecord, DNSService, HostState
import sys

class TestCreateDnsHostnameRecord(JinxTestCase):
    api_call_path = "/jinx/2.0/create_dns_hostname_record"

    def data(self):
        DNSRecord("jinx.lindenlab.com")

    def test_normal_call(self):
        response = self.do_api_call("hostname.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS hostname: hostname.lindenlab.com created successfully.")

    def test_bad_call(self):
        response = self.do_api_call("jinx.lindenlab.com")
        self.assert_response_code(response, 409)
        self.assertEqual(response.data, "DNS hostname record: jinx.lindenlab.com already exists.")
        

class TestCreateDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/create_dns_service_group"

    def data(self):
        DNSService("bacula")

    def test_normal_call(self):
        response = self.do_api_call("webservers")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS service group: webservers created successfully.")


    def test_bad_call(self):
        response = self.do_api_call("bacula")
        self.assert_response_code(response, 409)
        self.assertEqual(response.data, "DNS service group bacula already exists.")

class TestDeleteDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/delete_dns_service_group"

    def data(self):
        DNSService("test0")
        DNSService("test1")
        DNSRecord("host0.lindenlab.com")

        test0 = clusto.get_by_name("test0")
        host0 = clusto.get_by_name("host0.lindenlab.com")

        test0.insert(host0)

    def test_normal_call(self):
        response = self.do_api_call("test1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "Successfully deleted service group: test1.")

    def test_bad_call(self):
        response = self.do_api_call("test0")
        self.assert_response_code(response, 409)

class TestSetDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/set_dns_service_group"

    def data(self):
        group0 = DNSService("group0")
        group1 = DNSService("group1")
        jinx0 = DNSRecord("jinx0.lindenlab.com")
        jinx1 = DNSRecord("jinx1.lindenlab.com")

        group0.insert(jinx0)
        
    def test_normal_call(self):
        response = self.do_api_call("jinx1.lindenlab.com", "group1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS host record: jinx1.lindenlab.com successfully added to: group1 service group.")

    def test_bad_call(self):
        response = self.do_api_call("jinx0.lindenlab.com", "group0")
        self.assert_response_code(response, 409)
        self.assertEqual(response.data, "DNS host record: jinx0.lindenlab.com already exists in service group: group0.")

class TestUnsetDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/unset_dns_service_group"

    def data(self):
        group0 = DNSService("group0")
        group1 = DNSService("group1")
        jinx0 = DNSRecord("jinx0.lindenlab.com")
        jinx1 = DNSRecord("jinx1.lindenlab.com")

        group0.insert(jinx0)

    def test_normal_call(self):
        response = self.do_api_call("jinx0.lindenlab.com", "group0")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "Successfully removed: jinx0.lindenlab.com from dns service group: group0.")

    def test_bad_call(self):
        response = self.do_api_call("jinx1.lindenlab.com", "group1")
        self.assert_response_code(response, 409)
        self.assertEqual(response.data, "jinx1.lindenlab.com not found in dns service group: group1.")


class TestGetDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_service_group"

    def data(self):
        group1 = DNSService("test1")
        group2 = DNSService("test2")
        group3 = DNSService("test3")

        host = DNSRecord("jinx.lindenlab.com")
        group1.insert(host)
        group2.insert(host)
        group3.insert(host)

        
    def test_normal_call(self):
        response = self.do_api_call("jinx.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["test1", "test2", "test3"]))


class TestGetAllDnsServiceGroups(JinxTestCase):
    api_call_path = "/jinx/2.0/get_all_dns_service_groups"

    def data(self):
        group0 = DNSService("group0")
        group1 = DNSService("group1")
        group2 = DNSService("group2")

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["group0", "group1", "group2"]))


class TestGetDnsServiceGroupMembers(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_service_group_members"

    def data(self):
        group0 = DNSService("websters")

        host0 = DNSRecord("host0.lindenlab.com")
        host1 = DNSRecord("host1.lindenlab.com")
        host2 = DNSRecord("host2.lindenlab.com")

        group0.insert(host0)
        group0.insert(host1)
        group0.insert(host2)

    def test_normal_call(self):
        response = self.do_api_call("websters")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["host0.lindenlab.com", "host1.lindenlab.com", "host2.lindenlab.com"]))
