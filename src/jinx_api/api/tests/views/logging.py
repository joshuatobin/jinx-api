from api.tests.base import JinxTestCase
import clusto
import datetime
import llclusto
from llclusto.drivers import Class5Server, ServerClass, LogEventType

class TestAddLogEvent(JinxTestCase):
    api_call_path = "/jinx/2.0/add_log_event"

    def data(self):
        # Populate Clusto                                                                                                                            
        ServerClass("Class 5")
        Class5Server("hostname1")
        LogEventType("power on")

    def test_normal_call(self):
        response = self.do_api_call("hostname1", "dynamike", "power on")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)

        response = self.do_api_call("hostname1", "dynamike", "power on", "test descroption")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)

    def test_bad_hostname(self):
        response = self.do_api_call("hostname2", "dynamike", "power on")
        self.assert_response_code(response, 404)

    def test_bad_user(self):
        response = self.do_api_call("hostname1", 1, "power on")
        self.assert_response_code(response, 400)

    def test_bad_event_type(self):
        response = self.do_api_call("hostname1", "dynamike", "fake event")
        self.assert_response_code(response, 400)

        
class TestAddLogEventType(JinxTestCase):
    api_call_path = "/jinx/2.0/add_log_event_type"

    def data(self):
        LogEventType("power on")

    def test_normal_call(self):
        response = self.do_api_call("power off")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        response = self.do_api_call("power status", "Returns the power status of a host")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)


    def test_duplicate_event_type(self):
        response = self.do_api_call("power on")
        self.assert_response_code(response, 400)

    def test_bad_name(self):
        response = self.do_api_call(2)
        self.assert_response_code(response, 400)

class TestListLogEventTypes(JinxTestCase):
    api_call_path = "/jinx/2.0/list_log_event_types"
    
    def data(self):
        LogEventType("power on")
        LogEventType("power off")
        LogEventType("power status")

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), [{'name': 'power off', 'description': None},
                                                 {'name': 'power on', 'description': None}, 
                                                 {'name': 'power status', 'description': None}])

class TestGetLogEvents(JinxTestCase):
    api_call_path = "/jinx/2.0/get_log_events"

    def data(self):
        l1 = LogEventType("power on")
        ServerClass("Class 5")
        h1 = Class5Server("hostname1")
        h1.add_log_event(user="test1",
                         event_type=l1,
                         timestamp=datetime.datetime(2010, 1, 1, 1, 1, 1, 1),
                         description="test description")
        
    def test_normal_call(self):
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEquals(0, cmp(response.data[0], {'hostname': 'hostname1',
                                                    'event_type': 'power on',
                                                    'timestamp': '2010-01-01 01:01:01.000001',
                                                    'name': 'Log0000000001',
                                                    'user': 'test1',
                                                    'description': 'test description'}))
    def test_bad_hostname(self):
        response = self.do_api_call("invalid-hostname")
        self.assert_response_code(response, 404)
