from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import HostState
from jinx_api.api.models import DNSRecord, DNSService
import sys

class TestGetDnsRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_records_comments"

    def data(self):
        DNSRecord(name="jinx0.lindenlab.com", comment="Fancy new MX Record").save()
        DNSRecord(name="jinx1.lindenlab.com", comment="Fancy new MX Record").save()

    def test_normal_call(self):
        response = self.do_api_call(["jinx0.lindenlab.com", "jinx1.lindenlab.com"])
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted({'jinx0.lindenlab.com':'Fancy new MX Record', 'jinx1.lindenlab.com':'Fancy new MX Record'}))

class TestGetDnsRecordsServiceGroups(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_records_service_groups"

    def data(self):
        jinx0 = DNSRecord(name="jinx0.lindenlab.com", comment="Fancy new MX Record")
        jinx0.save()
        
        jinx1 = DNSRecord(name="jinx1.lindenlab.com", comment="Fancy new A Record")
        jinx1.save()

        jinx = DNSService(name="jinx", comment="Fancy Jinx group")
        jinx.save()

        jinx0.group = jinx
        jinx1.group = jinx

        jinx0.save()
        jinx1.save()
        jinx.save()

    def test_normal_call(self):
        response = self.do_api_call(["jinx0.lindenlab.com", "jinx1.lindenlab.com"])
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted({u'jinx': {u'description': u'Fancy Jinx group', u'members': [u'jinx0.lindenlab.com', u'jinx1.lindenlab.com']}}))

        
class TestGetDnsRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/get_dns_record_comment"

    def data(self):
        DNSRecord(name="crazyhost.lindenlab.com", comment="Crazy Comment!").save()

    def test_normal_call(self):
        response = self.do_api_call("crazyhost.lindenlab.com")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, "Crazy Comment!")

        record = DNSRecord.objects.get(name='crazyhost.lindenlab.com')
        self.assertEqual(record.comment, "Crazy Comment!")

class TestSetDnsRecordComment(JinxTestCase):
    api_call_path = "/jinx/2.0/set_dns_record_comment"

    def test_normal_call(self):
        response = self.do_api_call("crazyhost.lindenlab.com", "comment")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, True)
        
        
class TestCreateDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/create_dns_service_group"

    def data(self):
        DNSService(name="webster", comment="webster group").save()

    def test_normal_call(self):
        response = self.do_api_call("HWLB", "HWLB group")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, True)

        service = DNSService.objects.get(name='webster')
        self.assertEqual(service.name, 'webster')
        self.assertEqual(service.comment, 'webster group')
        
        
class TestSetDnsServiceGroup(JinxTestCase):
    api_call_path = "/jinx/2.0/set_dns_service_group"

    def data(self):
        DNSService(name="webster", comment="comment").save()

    def test_normal_call(self):
        response = self.do_api_call("web0.lindenlab.com", None)
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, True)

        response = self.do_api_call("web1.lindenlab.com", "webster")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, True)

    def test_bad_call(self):
        response = self.do_api_call("web", "fake comment")
        self.assert_response_code(response, 400)
        self.assertEqual(response.data, 'DNS service group: fake comment not found.')
        
        
        
        

        
