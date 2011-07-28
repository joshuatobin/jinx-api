from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import DNSRecord, DNSService, HostState
import sys

class TestAddDnsRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/add_dns_record_comment"

    def data(self):
        host = DNSRecord("jinx.lindenlab.com")
        host.comment = "new jinx A record"

    def test_normal_call(self):
        response = self.do_api_call("jinx.lindenlab.com", "Fancy New A Record Comment")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS comment added: Fancy New A Record Comment.") # Should overwrite the original comment

        response = self.do_api_call("jinx-staging.lindenlab.com", "new jinx MX record")
        self.assert_response_code(response, 200) # Should create the record and add a comment
        self.assertEqual(response.data, "DNS record and comment added: jinx-staging.lindenlab.com: new jinx MX record.") 

class TestGetDnsHostnameRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_hostname_record_comment"

    def data(self):
        host = DNSRecord("jinx.lindenlab.com")
        host.comment = "Fancy new MX Record"

    def test_normal_call(self):
        response = self.do_api_call("jinx.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "Fancy new MX Record")

class TestCreateDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/create_dns_service_group"

    def data(self):
        service = DNSService("bacula")
        service.comment = "new bacula comment"

    def test_normal_call(self):
        response = self.do_api_call("bacula", "Fancy New Comment")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS service added: Fancy New Comment.") # Should overwrite the original comment

        response = self.do_api_call("websters", "New Webster")
        self.assert_response_code(response, 200) # Should create the record and add a comment
        self.assertEqual(response.data, "DNS service and comment added: websters: New Webster.") 
        
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

class TestAddDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/add_dns_service_group"

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

class TestRemoveDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/remove_dns_service_group"

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


class TestGetDnsRecordServiceGroups(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_record_service_groups"

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


class TestGetDnsServiceGroupInfo(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_service_group_info"

    def data(self):
        group0 = DNSService("websters")
        group0.comment = "new comment"

        host0 = DNSRecord("host0.lindenlab.com")
        host1 = DNSRecord("host1.lindenlab.com")
        host2 = DNSRecord("host2.lindenlab.com")

        group0.insert(host0)
        group0.insert(host1)
        group0.insert(host2)

    def test_normal_call(self):
        response = self.do_api_call("websters")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), \
                             sorted({'description': 'new comment', 'members': ['host0.lindenlab.com', 'host1.lindenlab.com', 'host2.lindenlab.com']}))
