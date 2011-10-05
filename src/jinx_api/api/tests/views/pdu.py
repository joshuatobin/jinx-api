from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from api.tests.base import JinxTestCase
import clusto
from llclusto.drivers import LindenPDU, ServerClass, HostState, Class5Server
import sys

class TestGetPduHostnames(JinxTestCase):
    api_call_path = "/jinx/2.0/get_pdu_hostnames"

    def data(self):
        # Populate Clusto
        pdu1 = LindenPDU()
        pdu2 = LindenPDU()
        pdu1.hostname = "pdu1.lindenlab.com"
        pdu2.hostname = "pdu2.lindenlab.com"
    
    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), ["pdu1.lindenlab.com", "pdu2.lindenlab.com"])
        

