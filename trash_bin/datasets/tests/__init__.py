from django.test import TestCase
from datasets.models import RDataset

SERVER_NAME = "testserver"

class DatasetsTest_unauth(TestCase):

    def test_unauth_personal_list_get(self):
        """ can an unauth'd user retrieve a list of personal datasets? """
	""" expected: can't perform action """
        
        response = self.client.get("/datasets/yourdatasets/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/yourdatasets/")

    def test_unauth_public_list_get(self):
        """ can an unauth'd user retrieve a list of public datasets? """
	""" expected: can't perform action """
        
        response = self.client.get("/datasets/alldatasets/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/alldatasets/")

    def test_unauth_set_create(self):
        """ can an unauth'd user create a dataset? """
	""" expected: can't perform action """
        
        response = self.client.post("/datasets/create/", {
            "title": "TestDataset1",
	    "safety_level": 3,
	    "dataset_qty": 4,
            "caption": "Attempt to create a dataset by unauthorised user",
	    "tags": "",
	    "action": "create",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/create/")
	
    def test_unauth_see_set_details(self):
        """ can an unauth'd user see details of any dataset? """
	""" expected: can't perform action """
        
        response = self.client.get("/datasets/details/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/details/1/")

    def test_unauth_delete_dataset(self):
        """ can an unauth'd user delete datasets? """
	""" expected: can't perform action """
        
        response = self.client.get("/datasets/delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/delete/1/")
        response = self.client.post("/datasets/yourdatasets/", {
	    "set_choices": [1],
	    "action": "delete",
	})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datasets/yourdatasets/")
	

class DatasetsTest_auth(TestCase):
    fixtures = ["datasets.json"]

    """ For these tests we need pre-loaded data (see datasets.json).
    We want to model a situation with 3 users (Bob, Joe, Jane), and 2 
    datasets (both belong to Joe). The first set is private, but 
    has a specific share with Bob. The second set is friendly, and 
    has no specific privacy settings. Both datasets contain a set of 4
    files, with different security levels. Here we model cases to test
    some basic functions and system security."""

    def test_auth_dataset_create(self):
	""" Let's login as Bob and create a dataset. """

	# logging as Bob
        logged_in = self.client.login(username="bob", password="pass")
        self.assertTrue(logged_in)
        response = self.client.post("/datasets/create/", {
            "title": "BobDataset",
	    "safety_level": 3,
	    "dataset_qty": 4,
            "caption": "Attempt to create a dataset by authorised user Bob",
	    "tags": "",
	    "action": "create",
        })
	# created dataset should contain input data
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RDataset.objects.filter(title__contains='Bob').count(), 1)

    def test_auth_file_details_indep(self):
        """ Can Bob see Joe's dataset details or manage them? One dataset
	is specifically shared with Bob (1), another one (2) is not.
	Bob and Joe are not friends."""
        
	# logging as Bob
        logged_in = self.client.login(username="bob", password="pass")
        self.assertTrue(logged_in)
	# the first dataset should be accessible, as it's specifically shared
        response = self.client.get("/datasets/details/1/")
        self.assertEqual(response.status_code, 200)
	# Bob should not see inside 'private' and 'friendly' files
        self.assertContains(response, "JoeFile-Shared")
        self.assertContains(response, "JoeFile-Public")
        self.assertNotContains(response, "JoeFile-Private")
        self.assertNotContains(response, "JoeFile-Friendly")
	# the second dataset should NOT be accessible, it is 'friendly' but Bob is not a friend
        response = self.client.get("/datasets/details/2/")
        self.assertEqual(response.status_code, 404)
	# both datasets should not be manageable, as they belong to Joe
        response = self.client.post("/datasets/details/1/", {
            "title": "Bob changed dataset name",
	    "dataset_qty": 2,
            "caption": "Bob changed dataset description",
	    "tags": "Bob changed tags",
	    "action": "details_update",
        })
        self.assertNotContains(response, "Bob changed dataset name")
        self.assertNotContains(response, "Bob changed dataset description")
        self.assertNotContains(response, "Bob changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datasets/details/1/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(RDataset.objects.get(pk=1).safety_level, 3)
        self.assertEqual(RDataset.objects.get(pk=1).shared_with.all().count(), 1)
        self.assertEqual(str(RDataset.objects.get(pk=1).shared_with.all()[0].id), "1")
	# the second dataset even unavailable
        response = self.client.post("/datasets/details/2/", {
            "title": "Bob changed dataset name",
	    "dataset_qty": 2,
            "caption": "Bob changed dataset description",
	    "tags": "Bob changed tags",
	    "action": "details_update",
        })
        self.assertEqual(response.status_code, 404)
	# no way to delete datasets, as they belong to Joe  (10 - 'active' state)
        response = self.client.get("/datasets/delete/1/")
        self.assertEqual(RDataset.objects.get(pk=1).current_state, 10)
        response = self.client.get("/datasets/delete/2/")
        self.assertEqual(RDataset.objects.get(pk=2).current_state, 10)
        response = self.client.post("/datasets/yourdatasets/", {
	    "set_choices": [1, 2],
	    "action": "delete",
	})
        self.assertEqual(RDataset.objects.get(pk=1).current_state, 10)
        self.assertEqual(RDataset.objects.get(pk=2).current_state, 10)

    def test_auth_file_details_friend(self):
        """ Can Jane see Joe's files details or manage them? Jane is
	a Joe's friend."""
        
	# logging as Jane
        logged_in = self.client.login(username="jane", password="pass")
        self.assertTrue(logged_in)
	# the second dataset should be accessible, it is opened for 'friends'
        response = self.client.get("/datasets/details/2/")
        self.assertEqual(response.status_code, 200)
	# Jane should not see inside 'private' and 'shared' files
        self.assertContains(response, "JoeFile-Friendly")
        self.assertContains(response, "JoeFile-Public")
        self.assertNotContains(response, "JoeFile-Private")
        self.assertNotContains(response, "JoeFile-Shared")
	# the first dataset should NOT be accessible, it's private
        response = self.client.get("/datasets/details/1/")
        self.assertEqual(response.status_code, 404)
	# both datasets should not be manageable, as they belong to Joe
        response = self.client.post("/datasets/details/2/", {
            "title": "Jane changed dataset name",
	    "dataset_qty": 2,
            "caption": "Jane changed dataset description",
	    "tags": "Jane changed tags",
	    "action": "details_update",
        })
        self.assertNotContains(response, "Jane changed dataset name")
        self.assertNotContains(response, "Jane changed dataset description")
        self.assertNotContains(response, "Jane changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datasets/details/2/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(RDataset.objects.get(pk=1).safety_level, 3)
        self.assertEqual(RDataset.objects.get(pk=1).shared_with.all().count(), 1)
        self.assertEqual(str(RDataset.objects.get(pk=1).shared_with.all()[0].id), "1")
	# the first dataset even unavailable
        response = self.client.post("/datasets/details/1/", {
            "title": "Jane changed dataset name",
	    "dataset_qty": 2,
            "caption": "Jane changed dataset description",
	    "tags": "Jane changed tags",
	    "action": "details_update",
        })
        self.assertEqual(response.status_code, 404)
	# no way to delete datasets, as they belong to Joe  (10 - 'active' state)
        response = self.client.get("/datasets/delete/1/")
        self.assertEqual(RDataset.objects.get(pk=1).current_state, 10)
        response = self.client.get("/datasets/delete/2/")
        self.assertEqual(RDataset.objects.get(pk=2).current_state, 10)
        response = self.client.post("/datasets/yourdatasets/", {
	    "set_choices": [1, 2],
	    "action": "delete",
	})
        self.assertEqual(RDataset.objects.get(pk=1).current_state, 10)
        self.assertEqual(RDataset.objects.get(pk=2).current_state, 10)


    def test_owner_file_manage(self):
        """ Can Joe see his own datasets and manage them? Both datasets 
	(1) and (2) and files inside belong to him."""

	# logging as Joe
        logged_in = self.client.login(username="joe", password="pass")
        self.assertTrue(logged_in)
	# both my datasets should be accessible, verify the files inside
        response = self.client.get("/datasets/details/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "JoeFile-Private")
        self.assertContains(response, "JoeFile-Shared")
        self.assertContains(response, "JoeFile-Friendly")
        self.assertContains(response, "JoeFile-Public")
        response = self.client.get("/datasets/details/2/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "JoeFile-Private")
        self.assertContains(response, "JoeFile-Shared")
        self.assertContains(response, "JoeFile-Friendly")
        self.assertContains(response, "JoeFile-Public")
	# both files should not be manageable, as they belong to me (testing just one)
        response = self.client.post("/datasets/details/1/", {
            "title": "Joe changed dataset name",
	    "dataset_qty": 2,
            "caption": "Joe changed dataset description",
	    "tags": "Joe changed tags",
	    "action": "details_update",
        })
        self.assertContains(response, "Joe changed dataset name")
        self.assertContains(response, "Joe changed dataset description")
        self.assertContains(response, "Joe changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datasets/details/1/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(RDataset.objects.get(pk=1).safety_level, 1)
        self.assertEqual(RDataset.objects.get(pk=1).shared_with.all().count(), 2)
        self.assertEqual(str(RDataset.objects.get(pk=1).shared_with.all()[0].id), "1")
        self.assertEqual(str(RDataset.objects.get(pk=1).shared_with.all()[1].id), "3")
	# now I should be able to delete files, they are mine (20 - 'deleted' state)
        response = self.client.post("/datasets/yourdatasets/", {
	    "set_choices": [1],
	    "action": "delete",
	})
        self.assertEqual(RDataset.objects.get(pk=1).current_state, 20)
        response = self.client.get("/datasets/delete/2/")
        self.assertEqual(RDataset.objects.get(pk=2).current_state, 20)




