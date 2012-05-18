from django.test import TestCase
from datafiles.models import Datafile

SERVER_NAME = "testserver"

class DatafilesTest(TestCase):
    fixtures = ["datafiles.json"]

    """ For these tests we need pre-loaded data (see datafiles.json).
    We want to model a situation with 3 users (Bob, Joe, Jane), and 2 
    datafiles (both belong to Joe). The first file is private, but 
    has a specific share with Bob. The second file is friendly, and 
    has no specific privacy settings. Here we model different cases
    to test some basic functions and system security."""

    def test_unauth_personal_list_get(self):
        """ can an unauth'd user retrieve a list of personal files? """
	""" expected: can't perform action """
        
        response = self.client.get("/datafiles/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datafiles/")

    def test_unauth_public_list_get(self):
        """ can an unauth'd user retrieve a list of public files? """
	""" expected: can't perform action """
        
        response = self.client.get("/datafiles/alldatafiles/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datafiles/alldatafiles/")

    def test_unauth_file_create(self):
        """ can an unauth'd user upload a file? """
	""" expected: can't perform action """
        
	f = open('apps/datafiles/tests/Bach_WTC1_Richter_01.mp3')
	response = self.client.post('/datafiles/create/', {'title': 'TestFile1', 'raw_file': f})
	f.close()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datafiles/create/")
	
    def test_unauth_see_file_details(self):
        """ can an unauth'd user see files details? """
	""" expected: can't perform action """
        
        response = self.client.get("/datafiles/details/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datafiles/details/1/")

    def test_unauth_delete_file(self):
        """ can an unauth'd user delete files? """
	""" expected: can't perform action """
        
        response = self.client.get("/datafiles/delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "http://" + SERVER_NAME + "/account/login/?next=/datafiles/delete/1/")

    """
    This test is temporary omitted as it is related with 
    physical file upload.

    def test_auth_file_create(self):
        logged_in = self.client.login(username="bob", password="pass")
        self.assertTrue(logged_in)
	f = open('apps/datafiles/tests/Bach_WTC1_Richter_01.mp3')
        response = self.client.post("/datafiles/create/", {
            "title": "SecondFile",
	    "safety_level": 1,
            "raw_file": f
        })
	f.close()
        #self.assertEqual(response.status_code, 302)
        response = self.client.get("/datafiles/alldatafiles/")
	print response.content
        self.assertEqual(response.status_code, 200)"""

    def test_auth_file_details_indep(self):
        """ Can Bob see Joe's files details or manage them? One file
	is specifically shared with Bob (1), another one (2) is not.
	Bob and Joe are not friends."""
        
	# logging as Bob
        logged_in = self.client.login(username="bob", password="pass")
        self.assertTrue(logged_in)
	# the first file should be accessible, as it's specifically shared
        response = self.client.get("/datafiles/details/1/")
        self.assertEqual(response.status_code, 200)
	# the second file should NOT be accessible, it is 'friendly' but Bob doesn't have friends
        response = self.client.get("/datafiles/details/2/")
        self.assertEqual(response.status_code, 404)
	# both files should not be manageable, as they belong to Joe
        response = self.client.post("/datafiles/details/1/", {
            "title": "Bob changed the first file name",
	    "recording_date": "2010-02-15 19:11",
	    "initial-recording_date": "2010-02-15 19:11",
            "caption": "Bob changed the first file description",
	    "tags": "Bob changed tags",
	    "action": "details_update",
        })
        self.assertNotContains(response, "Bob changed the first file name")
        self.assertNotContains(response, "Bob changed the first file description")
        self.assertNotContains(response, "Bob changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datafiles/details/1/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(Datafile.objects.get(pk=1).safety_level, 3)
        self.assertEqual(Datafile.objects.get(pk=1).shared_with.all().count(), 1)
        self.assertEqual(str(Datafile.objects.get(pk=1).shared_with.all()[0].id), "1")
	# the second file even unavailable
        response = self.client.post("/datafiles/details/2/", {
            "title": "Bob changed the second file name",
	    "recording_date": "2010-02-15 19:11",
	    "initial-recording_date": "2010-02-15 19:11",
            "caption": "Bob changed the second file description",
	    "tags": "Bob changed tags",
	    "action": "details_update",
        })
        self.assertEqual(response.status_code, 404)
	# no way to delete files, as they belong to Joe  (10 - 'active' state)
        response = self.client.get("/datafiles/delete/1/")
        self.assertEqual(Datafile.objects.get(pk=1).current_state, 10)
        response = self.client.get("/datafiles/delete/2/")
        self.assertEqual(Datafile.objects.get(pk=2).current_state, 10)


    def test_auth_file_details_friend(self):
        """ Can Jane see Joe's files details or manage them? Jane is
	a Joe's friend."""
        
	# logging as Jane
        logged_in = self.client.login(username="jane", password="pass")
        self.assertTrue(logged_in)
	# the first file should NOT be accessible, it's private
        response = self.client.get("/datafiles/details/1/")
        self.assertEqual(response.status_code, 404)
	# the second file should be accessible, it is opened for 'friends'
        response = self.client.get("/datafiles/details/2/")
        self.assertEqual(response.status_code, 200)
	# both files should not be manageable, as they belong to Joe
        response = self.client.post("/datafiles/details/2/", {
            "title": "Jane changed the first file name",
	    "recording_date": "2010-02-15 19:11",
	    "initial-recording_date": "2010-02-15 19:11",
            "caption": "Jane changed the first file description",
	    "tags": "Jane changed tags",
	    "action": "details_update",
        })
        self.assertNotContains(response, "Jane changed the first file name")
        self.assertNotContains(response, "Jane changed the first file description")
        self.assertNotContains(response, "Jane changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datafiles/details/2/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(Datafile.objects.get(pk=2).safety_level, 2)
        self.assertEqual(Datafile.objects.get(pk=2).shared_with.all().count(), 0)
	# the first file even unavailable
        response = self.client.post("/datafiles/details/1/", {
            "title": "Jane changed the second file name",
	    "recording_date": "2010-02-15 19:11",
	    "initial-recording_date": "2010-02-15 19:11",
            "caption": "Jane changed the second file description",
	    "tags": "Jane changed tags",
	    "action": "details_update",
        })
        self.assertEqual(response.status_code, 404)
	# no way to delete files, as they belong to Joe  (10 - 'active' state)
        response = self.client.get("/datafiles/delete/1/")
        self.assertEqual(Datafile.objects.get(pk=1).current_state, 10)
        response = self.client.get("/datafiles/delete/2/")
        self.assertEqual(Datafile.objects.get(pk=2).current_state, 10)


    def test_owner_file_manage(self):
        """ Can Joe see his own files and manage them? Both files
	(1) and (2) belong to him."""

	# logging as Joe
        logged_in = self.client.login(username="joe", password="pass")
        self.assertTrue(logged_in)
	# both my files should be accessible
        response = self.client.get("/datafiles/details/1/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/datafiles/details/2/")
        self.assertEqual(response.status_code, 200)
	# both files should not be manageable, as they belong to me (testing just one)
        response = self.client.post("/datafiles/details/1/", {
            "title": "Joe changed the first file name",
	    "recording_date": "2010-02-15 19:11",
	    "initial-recording_date": "2010-02-15 19:11",
            "caption": "Joe changed the first file description",
	    "tags": "Joe changed tags",
	    "action": "details_update",
        })
        self.assertContains(response, "Joe changed the first file name")
        self.assertContains(response, "Joe changed the first file description")
        self.assertContains(response, "Joe changed tags")
	# attempt to modify privacy settings
        response = self.client.post("/datafiles/details/1/", {
            "safety_level": 1,
	    "shared_with": [1, 3],
	    "action": "privacy_update",
        })
        self.assertEqual(Datafile.objects.get(pk=1).safety_level, 1)
        self.assertEqual(Datafile.objects.get(pk=1).shared_with.all().count(), 2)
        self.assertEqual(str(Datafile.objects.get(pk=1).shared_with.all()[0].id), "1")
        self.assertEqual(str(Datafile.objects.get(pk=1).shared_with.all()[1].id), "3")
	# now I should be able to delete files, they are mine (20 - 'deleted' state)
        response = self.client.get("/datafiles/delete/1/")
        self.assertEqual(Datafile.objects.get(pk=1).current_state, 20)
        response = self.client.get("/datafiles/delete/2/")
        self.assertEqual(Datafile.objects.get(pk=2).current_state, 20)




