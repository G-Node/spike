from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from timeseries.models import TimeSeries
from apps.ext.odml.tools.xmlparser import XMLWriter, parseXML
from apps.ext.odml.doc import Document as odml_document
from apps.ext.odml.section import Section as odml_section
from apps.ext.odml.property import Property as odml_property

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

STATES = (
    (10, _('Active')),
    (20, _('Deleted')),
    (30, _('Archived')),
)

class Section(models.Model):
    """
    Class represents a metadata "Section". Used to organize experiment / dataset
     / file / timeseries metadata in a tree-like structure. May be linked to 
    Experiment, Dataset, File, Timeseries or itself.
    """
    current_state = models.IntegerField(_('state'), choices=STATES, default=10)
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    date_created = models.DateTimeField(_('date created'), default=datetime.now, editable=False)
    # links to the parent object. can be itself to create a tree.
    parent_exprt = models.ForeignKey(Experiment, null=True)
    parent_dataset = models.ForeignKey(RDataset, null=True)
    parent_datafile = models.ForeignKey(Datafile, null=True)
    parent_timeseries = models.ForeignKey(TimeSeries, null=True)
    parent_section = models.ForeignKey('self', null=True)
    # containers for links to key objects.
    rel_datasets = models.ManyToManyField(RDataset, related_name="sec_datasets", blank=True, verbose_name=_('related datasets'))
    rel_datafiles = models.ManyToManyField(Datafile, related_name="sec_datafiles",  blank=True, verbose_name=_('related datafiles'))
    rel_timeseries = models.ManyToManyField(TimeSeries, related_name="sec_timeseries", blank=True, verbose_name=_('related time series'))
    # position in the tree. to be able to move up and down
    tree_position = models.IntegerField(_('tree position'))
    # field indicates whether it is a "template" section
    is_template = models.BooleanField(_('is template'), default=False)
    # for "template" section this is a pointer to a user, who created this default
    # template. if "NULL" - all users see section as a "template" (odML vocabulary)
    user_custom = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_root(self):
        """
        Returns the root of the metadata tree ("odML document"), in other words,
        Experiment, or Dataset or etc., to which current metadata tree is 
        attached to.
        """
        if self.parent_section is not None:
            return self.parent_section.get_root()
        elif self.parent_exprt is not None:
            return self.parent_exprt
        elif self.parent_dataset is not None:
            return self.parent_dataset
        elif self.parent_datafile is not None:
            return self.parent_datafile
        elif self.parent_timeseries is not None:
            return self.parent_timeseries
        else:
            return None

    def get_owner(self):
        metadata_root = self.get_root()
        if metadata_root:
            return metadata_root.owner
        return None

    def does_belong_to(self, user):
        if self.get_owner() == user:
            return True
        return False

    def is_accessible(self, user):
        if not self.is_template:
            if not self.get_root().is_accessible(user):
                return False
        return True

    def get_tree(self, id_only=False):
        sec_tree = []
        sec_tree.append(self.id)
        if not id_only:
            sec_tree.append(self.title)
        if self.section_set.filter(current_state=10):
            for section in self.section_set.filter(current_state=10).order_by("tree_position"):
                sec_tree.append(section.get_tree(id_only))
        return sec_tree

    def get_tree_JSON(self):
        sec_tree = '"' + str(self.id) + '": { "ids": "'
        for section in self.section_set.filter(current_state=10).order_by("tree_position"):
            sec_tree += str(section.id) + ', '
        sec_tree += '", '
        if self.section_set.filter(current_state=10):
            for section in self.section_set.filter(current_state=10).order_by("tree_position"):
                sec_tree += section.get_tree_JSON()
        sec_tree += '}, '
        return sec_tree

    def get_parent(self):
        if self.parent_section:
            return self.parent_section
        else:
            if self.parent_exprt:
                return self.parent_exprt
            elif self.parent_dataset:
                return self.parent_dataset
            elif self.parent_datafile:
                return self.parent_datafile
            elif self.parent_timeseries:
                return self.parent_timeseries
        return None

    def get_active_properties(self, user=None):
        # no need to check the user for current version
        return self.property_set.filter(current_state=10)	    

    def get_active_datasets(self, user):
        datasets = self.rel_datasets.filter(current_state=10)
        datasets = filter(lambda x: x.is_accessible(user), datasets)
        return datasets
    def has_dataset(self, dataset_id):
        if self.rel_datasets.filter(current_state=10, id=dataset_id):
            return True
        return False

    def get_active_datafiles(self, user):
        datafiles = self.rel_datafiles.filter(current_state=10)
        datafiles = filter(lambda x: x.is_accessible(user), datafiles)
        return datafiles
    def has_datafile(self, datafile_id):
        if self.rel_datafiles.filter(current_state=10, id=datafile_id):
            return True
        return False

    def get_active_timeseries(self, user):
        timeseries = self.rel_timeseries.filter(current_state=10)
        timeseries = filter(lambda x: x.is_accessible(user), timeseries)
        return timeseries
    def has_timeserie(self, tserie_id):
        if self.rel_timeseries.filter(current_state=10, id=tserie_id):
            return True
        return False

    def has_child(self):
        """
        For the future.
        """
        pass

    def get_objects_count(self, r=True):
        """
        Returns sequence: datasets #, datafiles #, time series #, files volume
        Recursive, if r is True
        """
        files_vo = 0
        datasets_no = self.rel_datasets.filter(current_state=10).count()
        datafiles_no = self.rel_datafiles.filter(current_state=10).count()
        timeseries_no = self.rel_timeseries.filter(current_state=10).count()
        for f in self.rel_datafiles.filter(current_state=10):
            files_vo += f.raw_file.size
        if r:
            for section in self.section_set.all().filter(current_state=10):
                    s1, s2, s3, s4 = section.get_objects_count()
                    datasets_no += s1
                    datafiles_no += s2
                    timeseries_no += s3
                    files_vo += s4
        return datasets_no, datafiles_no, timeseries_no, files_vo

    def rename(self, new_title):
        self.title = new_title
        self.save()

    def deleteObject(self):
        if not self.current_state == 30: 
            self.current_state = 20
            self.save()
            return True
        return False

    def copy_section(self, section, pos, prnt=False):
        """
        Makes a copy of a given section, placing a copy into self.
        If prnt is True, then section stays at the top (root) of the document.
        """
        res_tree = []
        section_id = int(section.id)
        section.id = None
        section.parent_exprt = None
        section.parent_dataset = None
        section.parent_datafile = None
        section.parent_timeseries = None
        section.parent_section = None
        if prnt:
            # parent object is not a Section
            prn_obj = self.get_parent()
            if isinstance(prn_obj, Experiment):
                section.parent_exprt = prn_obj
            elif isinstance(prn_obj, RDataset):
                section.parent_dataset = prn_obj
            elif isinstance(prn_obj, Datafile):
                section.parent_datafile = prn_obj
            elif isinstance(prn_obj, TimeSeries):
                section.parent_timeseries = prn_obj
        else:
            section.parent_section = self
        section.tree_position = pos
        section.is_template = 0
        #section.date_created = datetime.now # setup later
        section.save()
        cp_section = Section.objects.get(id=section_id)
        new_id = section.id
        res_tree.append(new_id)
        # copy all properties
        for prop in cp_section.get_active_properties():
            prop.id = None
            prop.parent_section = new_id
            #prop.prop_date_created = datetime.now # setup later
            prop.save()
            prop.setParent(new_id)
        # copy all linked objects
        for dataset in cp_section.rel_datasets.filter(current_state=10):
            section.addLinkedObject(dataset, "dataset")
        for datafile in cp_section.rel_datafiles.filter(current_state=10):
            section.addLinkedObject(datafile, "datafile")
        for timeseries in cp_section.rel_timeseries.filter(current_state=10):
            section.addLinkedObject(timeseries, "timeseries")
        section.save()

        # recursively copy sections inside
        for sec in cp_section.section_set.filter(current_state=10).order_by("tree_position"):
            # this is to exclude self-recursion
            if not (sec.id == section.id):
                res_tree.append(section.copy_section(sec, sec.tree_position))
        return res_tree

    def increaseTreePos(self):
        self.tree_position += 1
        self.save()

    def clean_parent(self):
        self.parent_section = None
        self.parent_exprt = None
        self.parent_dataset = None
        self.parent_datafile = None
        self.parent_timeseries = None
        self.save()

    def addLinkedObject(self, obj, obj_type):
        if obj_type == "dataset":
            self.rel_datasets.add(obj)
        elif obj_type == "datafile":
            self.rel_datafiles.add(obj)
        elif obj_type == "timeseries":
            self.rel_timeseries.add(obj)

    def removeLinkedObject(self, obj, obj_type):
        if obj_type == "dataset":
            self.rel_datasets.remove(obj)
        elif obj_type == "datafile":
            self.rel_datafiles.remove(obj)
        elif obj_type == "timeseries":
            self.rel_timeseries.remove(obj)

    # odML import/export

    def _get_next_tree_pos(self):
        """
        Returns the next free index "inside" self.
        """
        sec_childs = self.section_set.all().order_by("-tree_position")
        if sec_childs:
            tree_pos = int(sec_childs.all()[0].tree_position) + 1
        else:
            tree_pos = 1
        return tree_pos

    def _import_section(self, section):
        """
        Imports one section from the odML section.
        """
        tree_pos = self._get_next_tree_pos()
        s = Section(title=section.name, parent_section=self, tree_position=tree_pos)
        s.save()
        # saving properties
        for p in section.properties:
            new_p = Property(prop_title=p.name, prop_value=str(p.values), \
                prop_parent_section=s)
            new_p.save()
        # recursively saving other sections
        for i in section.sections:
            s._import_section(i)

    def _import_xml(self, xml_file):
        """
        Parses given XML file and imports sections/properties. Uses odML parser.
        """
        data = parseXML(xml_file)
        #raise Exception("The file provided is not XML or is corrupted.")
        for s in data.sections:
            self._import_section(s)

    def _export_section(self):
        """
        Exports one section into odML section, including properties.
        """
        s = odml_section(name=self.title)
        s.type = "undefined"
        for p in self.property_set.all():
            prop = odml_property(name=p.prop_title, value=p.prop_value)
            s.append(prop)
        for sec in self.section_set.filter(current_state=10).order_by("tree_position"):
            s.append(sec._export_section())
        return s

    def _export_xml(self):
        """
        Exports self with all children and properties. Uses odML parser.
        """
        doc = odml_document()
        for s in self.section_set.filter(current_state=10).order_by("tree_position"):
            doc.append(s._export_section())
        wrt = XMLWriter(doc)
        return wrt.header + wrt.__unicode__()


class Property(models.Model):
    """
    Class represents a metadata "Property". Defines any kind of metadata 
    property and may be linked to the Section.
    """
    current_state = models.IntegerField(_('state'), choices=STATES, default=10)
    prop_title = models.CharField(_('title'), max_length=100)
    prop_value = models.TextField(_('value'), blank=True)
    prop_description = models.TextField(_('description'), blank=True)
    prop_name_definition = models.TextField(_('name_definition'), blank=True)
    prop_comment = models.TextField(_('comment'), blank=True)
    prop_date_created = models.DateTimeField(_('date created'), default=datetime.now, editable=False)
    prop_parent_section = models.ForeignKey(Section, blank=True)

    def __unicode__(self):
        return self.title

    @property
    def title(self):
        return self.prop_title

    def does_belong_to(self, user):
        """
        Defines whether this property belongs to a certain user.
        """
        section = self.prop_parent_section
        if section.does_belong_to(user):
            return True
        else:
            return False

    def update(self, title, value, description, comment, definition):
        if title:
            self.prop_title = title
        if value:
            self.prop_value = value
        if description:
            self.prop_description = description
        if comment:
            self.prop_comment = comment
        if definition:
            self.prop_name_definition = definition

    def setParent(self, par_id):
        self.prop_parent_section = Section.objects.get(id=par_id)
        self.save()

    def deleteObject(self):
        if not self.current_state == 30: 
            self.current_state = 20
            self.save()
            return True
        return False


