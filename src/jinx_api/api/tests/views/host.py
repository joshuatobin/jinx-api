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

