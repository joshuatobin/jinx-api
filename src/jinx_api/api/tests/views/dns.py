from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import HostState
from jinx_api.api.models import DNSRecord, DNSService
import sys

class TestAddDnsRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/add_dns_record_comment"

    def data(self):
        DNSRecord(name="jinx.lindenlab.com", comment="new jinx A record").save()
        
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
        DNSRecord(name="jinx.lindenlab.com", comment="Fancy new MX Record").save()

    def test_normal_call(self):
        response = self.do_api_call("jinx.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "Fancy new MX Record")

class TestCreateDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/create_dns_service_group"

    def data(self):
        DNSService(name="bacula", comment="new bacula comment").save()

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
        test0 = DNSService(name="test0")
        test0.save()
        
        test1 = DNSService(name="test1")
        test1.save()
        
        host0 = DNSRecord(name="host0.lindenlab.com")

        host0.group = test0
        host0.save()

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
        group0 = DNSService(name="group0")
        group1 = DNSService(name="group1")
        jinx0 = DNSRecord(name="jinx0.lindenlab.com")
        jinx1 = DNSRecord(name="jinx1.lindenlab.com")

        jinx0.group = group0

        group0.save()
        group1.save()
        jinx0.save()
        jinx1.save()
        
    def test_normal_call(self):
        response = self.do_api_call("jinx1.lindenlab.com", "group1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS host record: jinx1.lindenlab.com successfully added to: group1 service group.")

    def test_normal_call(self):
        response = self.do_api_call("jinx3.lindenlab.com", "group1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "DNS host record: jinx3.lindenlab.com successfully added to: group1 service group.")

class TestRemoveDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/remove_dns_service_group"

    def data(self):
        group0 = DNSService(name="group0")
        group0.save()

        group1 = DNSService(name="group1")
        group1.save()
        
        jinx0 = DNSRecord(name="jinx0.lindenlab.com")
        jinx1 = DNSRecord(name="jinx1.lindenlab.com")

        jinx0.group = group0
        jinx0.save()

        jinx1.save()

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
        group1 = DNSService(name="test1")
        group1.save()

        group2 = DNSService(name="test2")
        group2.save()

        host0 = DNSRecord(name="jinx0.lindenlab.com")
        host0.group = group1
        host0.save()
        
    def test_normal_call(self):
        response = self.do_api_call("jinx0.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, ["test1"])

class TestGetAllDnsServiceGroups(JinxTestCase):
    api_call_path = "/jinx/2.0/get_all_dns_service_groups"

    def data(self):
        DNSService(name="group0").save()
        DNSService(name="group1").save()
        DNSService(name="group2").save()

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["group0", "group1", "group2"]))


class TestGetDnsServiceGroupInfo(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_service_group_info"

    def data(self):
        group0 = DNSService(name="websters", comment="new comment")
        group0.save()
        
        host0 = DNSRecord(name="host0.lindenlab.com")
        host1 = DNSRecord(name="host1.lindenlab.com")
        host2 = DNSRecord(name="host2.lindenlab.com")

        host0.group = group0
        host1.group = group0
        host2.group = group0

        host0.save()
        host1.save()
        host2.save()

    def test_normal_call(self):
        response = self.do_api_call("websters")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), \
                             sorted({'description': 'new comment', 'members': ['host0.lindenlab.com', 'host1.lindenlab.com', 'host2.lindenlab.com']}))


class TestGetDnsRecordsComments(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_records_comments"

    def data(self):
        DNSRecord(name="host0.lindenlab.com", comment="host 0 comment").save()
        DNSRecord(name="host1.lindenlab.com", comment="host 1 comment").save()
        DNSRecord(name="host2.lindenlab.com", comment="host 2 comment").save()

    def test_normal_call(self):
        response = self.do_api_call(['host0.lindenlab.com', 'host1.lindenlab.com', 'host2.lindenlab.com'])
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), \
                             sorted({'host0.lindenlab.com':'host 0 comment',\
                                     'host1.lindenlab.com':'host 1 comment',\
                                     'host2.lindenlab.com':'host 2 comment'}))

    def test_bad_call(self):
        response = self.do_api_call('some bad string')
        self.assert_response_code(response, 400) # should throw a 400 if a list isn't passed.


class TestGetDnsServiceGroupMembersInfo(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_service_group_members_info"

    def data(self):
        host0 = DNSRecord(name="jinx0.lindenlab.com")
        host0.comment = "comments"

        host1 = DNSRecord(name="jinx1.lindenlab.com")
        host1.comment = "comments"



        group = DNSService(name="jinx", comment="Hosts Group")
        group.save()

        group0 = DNSService(name="bacula", comment="Hosts Group")
        group0.save()

        host0.group = group
        host0.save()

        host1.group = group0
        host1.save()
    def test_normal_call(self):
        response = self.do_api_call(['jinx0.lindenlab.com', 'jinx1.lindenlab.com'])
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted({u'bacula': {u'description': u'Hosts Group', u'members': \
                                                            [u'jinx1.lindenlab.com']}, \
                                                 u'jinx': {u'description': u'Hosts Group', u'members': \
                                                             [u'jinx0.lindenlab.com']}}))
