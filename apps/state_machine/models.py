from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from friends.models import Friendship

class MetadataManager:
    """
    Class to represent some common methods, applicable for "metadata" (for 
    Datafiles, Datasets etc.)
    """
    def get_metadata(self):
        metadata = []
        for section in self.section_set.filter(current_state=10).order_by("tree_position"):
            metadata.append(section.get_tree())
        return metadata

    def get_metadata_root_id(self):
        """
        Method is needed to keep the first level of metadata tree opened.
        """
        if self.section_set.filter(current_state=10):
            return self.section_set.filter(current_state=10)[0].id
        else:
            return None

    def has_metadata(self):
        if self.section_set.filter(current_state=10):
            return True
        return False

    def objects_count(self):
        """
        Number of 'linked' (through odML sections) objects - datasets, files etc.
        """
        datasets_no = 0
        datafiles_no = 0
        timeseries_no = 0
        files_vo = 0
        sections = self.section_set.all().filter(current_state=10)
        for sec in sections:
            s1, s2, s3, s4 = sec.get_objects_count()
            datasets_no += s1
            datafiles_no += s2
            timeseries_no += s3
            files_vo += s4
        return datasets_no, datafiles_no, timeseries_no, files_vo

    def objects_count_str(self):
        s1, s2, s3, s4 = self.objects_count()
        result = ""
        if s1: result = "Datasets (" + str(s1) + "), "
        if s2: result = result + "Files (" + str(s2) + "), "
        if s3: result = result + "Time Series (" + str(s3) + "), "
        if result: result = result[:len(result)-2]
        return result

class LinkedToProject:
    """
    Class represents methods to link an object (e.g. Dataset or Experiment) to a 
    Project. An object (self) must contain a field (in_projects) to store links.
    """
    def add_linked_project(self, project):
        try:
            self.in_projects.add(project)
        except BaseException:
            raise "This Django object doesn't have a container for links to projects."

    def remove_linked_project(self, project):
        try:
            self.in_projects.remove(project)
        except BaseException:
            raise "This Django object doesn't have a container for links to projects."


class ObjectState(models.Model):
    """
    A Simple G-Node-State base representation for other classes (e.g. Datasets,
    Experiments, Files etc.) An object can be Active, Deleted and Archived, 
    usually with the following cycle

    Active <--> Deleted -> Archived

    """
    STATES = (
        (10, _('Active')),
        (20, _('Deleted')),
        (30, _('Archived')),
    )
    current_state = models.IntegerField(_('state'), choices=STATES, default=10)
    
    def getCurrentState():
        return self.current_state

    def restoreObject(self):
        self.current_state = 10

    def deleteObject(self):
        self.current_state = 20

    def moveToArchive(self):
        try:
            self.current_state = 30
        except BaseException:
            raise KeyError("Object can't be moved to archive. Check \
                dependencies or it's a developer issue.")

    def isActive(self):
        return self.current_state == 10


class SafetyLevel(ObjectState):
    """
    Safety level represents a level of access to an object by other users. An 
    object can be Public (all users have access), Friendly (all "friends" have 
    access) and Private (owner and special assignments only). Also handles 
    special assignments (access for special users from the list).
    """

    SAFETY_LEVELS = (
        (1, _('Public')),
        (2, _('Friendly')),
        (3, _('Private')),
    )

    safety_level = models.IntegerField(_('privacy level'), choices=SAFETY_LEVELS, default=3)
    shared_with = models.ManyToManyField(User, blank=True, verbose_name=_('share with'))
    
    def shareObject(users_list):
        self.shared_with = users_list

    def getSharedWithList():
        return self.shared_with

    def removePrivateShares():
        self.shared_with.clear()

    def publishObject():
        self.safety_level = 1
        # add some special handliers for publications here

    def setSafetyLevel(safety_level):
        if safety_level in [1,2,3]:
            self.safety_level = safety_level
        else:
            raise KeyError("Wrong safety level type")

    def is_Public(self):
        return self.safety_level == 1

    def is_Friendly(self):
        return self.safety_level == 2

    def is_Private(self):
        return self.safety_level == 3

    def is_accessible(self, user):
        """
        Defines whether a "parent" object (e.g. Datafile) is accessible for a 
        given user. 
        """
        try:
            if (self.owner == user) or (self.is_Public()) or \
                (user in self.shared_with.all()) or (self.is_Friendly() and \
                    Friendship.objects.are_friends(user, self.owner)):
                return True
        except BaseException:
            raise KeyError("Object has no Friends or no Owner. Can't identify accessibility.")
        return False

