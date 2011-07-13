from api.tests.base import JinxTestCase
import clusto
import llclusto
from llclusto.drivers import Class5Server, ServerClass, HostState, PGIImage
import sys

class TestListServablePGIImages(JinxTestCase):
    api_call_path = "/jinx/2.0/list_servable_pgi_images"
    
    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        self.image1 = PGIImage("test image1")
        self.image2 = PGIImage("test image2")
        self.host1.add_stored_pgi_image(self.image1)
        self.host2.add_stored_pgi_image(self.image2)

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["test image1", "test image2"]))
        self.image3 = PGIImage("test image3")
        self.host1.add_stored_pgi_image(self.image3)
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["test image1", "test image2", "test image3"]))


class TestGetHostsWithImage(JinxTestCase):
    api_call_path = "/jinx/2.0/get_hosts_with_image"
    
    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        image1 = PGIImage("test image1")
        self.host1.pgi_image = image1
        self.host2.pgi_image = image1

    def test_normal_call(self):
        response = self.do_api_call("test image1")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["hostname1", "hostname2"]))

    def test_bad_call(self):
        response = self.do_api_call("test image2")
        self.assert_response_code(response, 404)


class TestListHostImageAssociations(JinxTestCase):
    api_call_path = "/jinx/2.0/list_host_image_associations"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        self.host3 = Class5Server("hostname3")
        image1 = PGIImage("test image1")
        image2 = PGIImage("test image2")        
        self.host1.pgi_image = image1
        self.host2.pgi_image = image2
        self.host3.pgi_image = image1

    def test_normal_call(self):
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'hostname1': 'test image1', 
                                         'hostname2': 'test image2', 
                                         'hostname3': 'test image1'})
        image3 = PGIImage("test image3")
        self.host3.pgi_image = image3
        response = self.do_api_call()
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {'hostname1': 'test image1',
                                         'hostname2': 'test image2',
                                         'hostname3': 'test image3'})


class TestGetCurrentPGIImage(JinxTestCase):
    api_call_path = "/jinx/2.0/get_current_pgi_image"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        image1 = PGIImage("test image1")
        self.host1.pgi_image = image1

    def test_normal_call(self):
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {"hostname1": "test image1"})
        image2 = PGIImage("test image2")
        self.host1.pgi_image = image2
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {"hostname1": "test image2"})
        response = self.do_api_call("hostname2")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {})
        
    def test_bad_call(self):
        # hostname3 does not exist
        response = self.do_api_call("hostname3")
        self.assert_response_code(response, 404)

        
class TestGetPreviousPGIImage(JinxTestCase):
    api_call_path = "/jinx/2.0/get_previous_pgi_image"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        image1 = PGIImage("test image1")
        image2 = PGIImage("test image2")
        self.host1.pgi_image = image1
        self.host1.pgi_image = image2

    def test_normal_call(self):
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {"hostname1": "test image1"})

        image3 = PGIImage("test image3")
        self.host1.pgi_image = image3
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {"hostname1": "test image2"})

        response = self.do_api_call("hostname2")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, {})

    def test_bad_call(self):
        # hostname3 does not exist
        response = self.do_api_call("hostname3")
        self.assert_response_code(response, 404)


class TestUpdateHostImageAssociation(JinxTestCase):
    api_call_path = "/jinx/2.0/update_host_image_association"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.image1 = PGIImage("test image1")

    def test_normal_call(self):
        response = self.do_api_call("hostname1", "test image1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.pgi_image, self.image1)
        self.image2 = PGIImage("test image2")
        response = self.do_api_call("hostname1", "test image2")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.pgi_image, self.image2)

    def test_bad_call(self):
        #hostname2 does not exist
        response = self.do_api_call("hostname2", "test image1")
        self.assert_response_code(response, 404)
        # test image3 does not exist
        response = self.do_api_call("hostname1", "test image3")
        self.assert_response_code(response, 404)


class TestRollbackHostImage(JinxTestCase):
    api_call_path = "/jinx/2.0/rollback_host_image"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.image1 = PGIImage("test image1")
        self.image2 = PGIImage("test image2")
        self.host1.pgi_image = self.image1
        self.host1.pgi_image = self.image2

    def test_normal_call(self):
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.pgi_image, self.image1)
        self.image3 = PGIImage("test image3")
        self.host1.pgi_image = self.image3
        self.host1.pgi_image = self.image2
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.pgi_image, self.image3)

    def test_bad_call(self):
        # hostname2 does not exist
        response = self.do_api_call("hostname2")
        self.assert_response_code(response, 404)
        self.host2 = Class5Server("hostname2")
        # hostname2 does not have an image to rollback too
        self.host2.pgi_image = self.image1
        response = self.do_api_call("hostname2")
        self.assert_response_code(response, 409)
        

class TestGetSIImages(JinxTestCase):
    api_call_path = "/jinx/2.0/get_si_images"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.host2 = Class5Server("hostname2")
        self.host3 = Class5Server("hostname3")
        self.image1 = PGIImage("test image1")
        self.image2 = PGIImage("test image2")
        self.host1.add_stored_pgi_image(self.image1)
        self.host1.add_stored_pgi_image(self.image2)
        self.host2.add_stored_pgi_image(self.image1)

    def test_normal_call(self):
        response = self.do_api_call("hostname1")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["test image1", "test image2"]))
        response = self.do_api_call("hostname2")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted(["test image1"]))
        response = self.do_api_call("hostname3")
        self.assert_response_code(response, 200)
        self.assertEqual(sorted(response.data), sorted([]))

    def test_bad_call(self):
        # hostname4 does not exist
        response = self.do_api_call("hostname4")
        self.assert_response_code(response, 404)


class TestDeleteSIImage(JinxTestCase):
    api_call_path = "/jinx/2.0/delete_si_image"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.image1 = PGIImage("test image1")
        self.image2 = PGIImage("test image2")
        self.host1.add_stored_pgi_image(self.image1)
        self.host1.add_stored_pgi_image(self.image2)

    def test_normal_call(self):
        response = self.do_api_call("hostname1", "test image1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(sorted(self.host1.get_stored_pgi_images()), sorted([self.image2]))
        response = self.do_api_call("hostname1", "test image2")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.get_stored_pgi_images(), [])

    def test_bad_call(self):
        # hostname2 does not exist
        response = self.do_api_call("hostname2", "test image1")
        self.assert_response_code(response, 404)

        # test image3 does not exist
        response = self.do_api_call("hostname1", "test image3")
        self.assert_response_code(response, 404)
        
        # test image1 is associated with a host
        self.host2 = Class5Server("hostname2")
        self.host2.pgi_image = self.image1
        response = self.do_api_call("hostname1", "test image1")
        self.assert_response_code(response, 409)

        # test image3 is not stored on hostname1
        self.image3 = PGIImage("test image3")
        response = self.do_api_call("hostname1", "test image3")
        self.assert_response_code(response, 404)


class TestAddSIImage(JinxTestCase):
    api_call_path = "/jinx/2.0/add_si_image"

    def data(self):
        HostState("up")
        ServerClass("Class 5")
        self.host1 = Class5Server("hostname1")
        self.image1 = PGIImage("test image1")
        self.image2 = PGIImage("test image2")

    def test_normal_call(self):
        response = self.do_api_call("hostname1", "test image1")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(self.host1.get_stored_pgi_images(), [self.image1])
        response = self.do_api_call("hostname1", "test image2")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.assertEqual(sorted(self.host1.get_stored_pgi_images()), sorted([self.image1, self.image2]))
        response = self.do_api_call("hostname1", "test image3")
        self.assert_response_code(response, 200)
        self.assertEqual(response.data, None)
        self.image3 = clusto.get_by_name("test image3")
        self.assertEqual(sorted(self.host1.get_stored_pgi_images()), sorted([self.image1, self.image2, self.image3]))

    def test_bad_call(self):
        #hostname2 does not exist
        response = self.do_api_call("hostname2", "test image4")
        self.assert_response_code(response, 404)

