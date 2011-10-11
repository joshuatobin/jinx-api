from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from django.conf import settings
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
        


class TestPowerManage(JinxTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='opsuser', password='password1')
        self.dnocuser = User.objects.create(username='dnocuser', password='password1')

        self.opsgroup = Group.objects.create(name='ops')

        flip_perm = Permission.objects.get(codename='flip_databases')
        view_power_manage = Permission.objects.get(codename='view_power_manage')
        
        self.opsgroup.permissions.add(flip_perm)
        self.opsgroup.permissions.add(view_power_manage)

        self.user1.groups.add(self.opsgroup)

        self.user1.save()
        self.opsgroup.save()
        self.dnocuser.save()

    def test_group_membership(self):
        self.assertEqual(self.user1.username, 'opsuser')
        self.assertEqual(self.user1.has_perm('api.flip_databases'), True)
        self.assertEqual(self.dnocuser.has_perm('api.flip_databases'), False)
        self.assertEqual(self.user1.has_perm('api.view_power_manage'), True)

    def test_view(self):
        c = Client()
        response = c.get('/ui/')
        self.assertEqual(response.status_code, 200)
        
        response = c.get('/ui/power-manage', {'username': 'opsuser', 'password':'password1'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user1.delete()
        self.opsgroup.delete()
        self.dnocuser.delete()

        
        
