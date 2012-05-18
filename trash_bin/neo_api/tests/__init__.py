"""
Tests Roadmap
================================================================================
- unauthorized tests
- generic tests: 
    - create
    - get full, info, data, parents, children
    - update + get
    - select
- bad requests tests: assert correct bad data handling for all types of requests
- security tests: try to access objects created by another person

Still remaining:
- size, slicing, downsampling, unicode etc.
- data consistency tests: post/get data values do not differ significantly
- wrong URLs
- performance tests!!
- cascade
- Etag + last-modified
"""

from django.test import TestCase
from neo_api.models import *
from neo_api.tests.samples import sample_objects
from neo_api.json_builder import clean_attr
from neo_api.meta import meta_attributes
try:
    import json
except ImportError:
    import simplejson as json

SERVER_NAME = "testserver"

class TestUnauthorized(TestCase):
    # TODO update that to test all the objects
    def test_unauth_create(self):
        """ test: create a block """
        """ expected: 401 Unathorized """
        response = self.client.post("/neo/block/", {
            "name": "Block of recordings from May, 10",
            "filedatetime": "2011-10-05",
            "index": 1
        })
        self.assertEqual(response.status_code, 401)

    def test_unauth_update(self):
        """ test: update a block """
        """ expected: 401 Unathorized """
        response = self.client.post("/neo/block/1/", {
            "index": 5
        })
        self.assertEqual(response.status_code, 401)

    def test_unauth_get(self):
        """ test: get single object """
        """ expected: 401 Unathorized """
        response = self.client.get("/neo/block/1/")
        self.assertEqual(response.status_code, 401)


class TestGeneric(TestCase):
    fixtures = ["users.json", "samples.json"]

    def setUp(self):
        logged_in = self.client.login(username="bob", password="pass")
        self.assertTrue(logged_in)

    def test_create_objects(self):
        """
        Test of successful creation of all types of NEO objects.
        expected: 201 created
        """
        for obj_type, obj in sample_objects.items():
            for i in range(5): # create a few objects
                response = self.client.post("/neo/%s/" % obj_type, \
                    json.dumps(obj), content_type="application/json")
                self.assertEqual(response.status_code, 201, \
                    "Obj type %s; response: %s" % (obj_type, response.content))
                    # "{0}, {1}".format(response.content, obj["obj_type"])) no python 2.6 (((

    def test_get_object(self):
        """
        Test the GET single object URLs.
        expected: 200 successful
        """
        for key in sample_objects.keys():
            response = self.client.get("/neo/%s/1/" % key)
            self.assertEqual(response.status_code, 200, \
                "Obj type %s; response: %s" % (key, str(response)))
            self.assertContains(response, key) # TODO add full check

    def test_update_objects(self):
        """
        Test of successful update of all attributes.
        expected: 200 successful
        """
        """
        for key, obj in sample_objects.items():
            # some of these are already created from fixtures
            response = self.client.post("/neo/", json.dumps(obj), \
                content_type="application/json")
            self.assertEqual(response.status_code, 201)
            for _attr in meta_attributes[key]:
                attr = clean_attr(_attr)
                post = {}
                post["neo_id"] = obj[key + "_1"] # should be created with 1 or 2
                post[attr] = obj[attr] # assign new attr
        """
        pass # TODO

    def test_select_objects(self):
        """
        Test to retreive list of objects.
        expected: 200 successful, number of objects is correct
        """
        for key in sample_objects.keys():
            response = self.client.get("/neo/%s/" % key)
            self.assertEqual(response.status_code, 200, \
                "Obj type %s; response: %s" % (key, str(response)))
            r = json.loads(response.content)
            self.assertEqual(len(r["selected"]), 1) # from fixtures
            # TODO more convenient checks?
            

class TestSecurity(TestCase):
    """
    Here we test that a fake user 'joe' can't access objects, created (with
    fixtures) by another fake user 'bob'. More tests here, when object sharing 
    is implemented.
    """

    fixtures = ["users.json", "samples.json"]

    def setUp(self):
        logged_in = self.client.login(username="joe", password="pass")
        self.assertTrue(logged_in)

    def test_access_alien(self):
        for key in sample_objects.keys():
            # all IDs from fixtures are just <object_type>_1
            response = self.client.get("/neo/%s/1/" % key)
            self.assertEqual(response.status_code, 401)

    def test_update_alien(self):
        for key, obj in sample_objects.items():
            # all alien object IDs are just <object_type>_1
            response = self.client.post("/neo/%s/1/" % key, json.dumps(obj), \
                content_type="application/json")
            self.assertEqual(response.status_code, 401)



