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

        response = self.do_api_call("hostname1", "dynamike", "power on", "test description")
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
        self.assert_response_code(response, 404)

        
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
        self.assert_response_code(response, 409)

    def test_bad_name(self):
        response = self.do_api_call(2)
        self.assert_response_code(response, 400)

class TestListLogEventTypes(JinxTestCase):
    api_call_path = "/jinx/2.0/list_log_event_types"
    
    def data(self):
        l1 = LogEventType("power on")
        l1.description = "Powers host on."
        l2 = LogEventType("power off")
        l2.description = "Powers host off."
        l3 = LogEventType("power status")
        l3.description = "Returns current power status."

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(cmp(response.data, {'power off' : "Powers host off.",
                                             'power on' : "Powers host on.",
                                             'power status' : "Returns current power status."}), 0)

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
        response = self.do_api_call("hostname1",
                                    "test1",
                                    "power on",
                                    datetime.datetime(2000, 1, 1, 1, 1, 1, 1),
                                    datetime.datetime(2020, 1, 1, 1, 1, 1, 1))
        self.assert_response_code(response, 200)
        self.assertEquals(response.data, [{u'event_type': u'power on', 
                                           u'timestamp': datetime.datetime(2010, 1, 1, 1, 1, 1, 1), 
                                           u'hostname': u'hostname1', 
                                           u'name': u'Log0000000001', 
                                           u'user': u'test1', 
                                           u'description': u'test description'}])

    def test_bad_hostname(self):
        response = self.do_api_call(2)
        self.assert_response_code(response, 404)
        
    def test_bad_entity_type(self):
        response = self.do_api_call(None, None, 2)
        self.assert_response_code(response, 404)

    def test_bad_timestamp(self):
        response = self.do_api_call(None, None, None, 2)
