# common imports
from datafiles.models import Datafile
from celery.decorators import task

import neuroshare as ns
from neuroshare.Library import ArgumentError, DLLTypeUnknown, DLLNotFound
try:
    import json
except ImportError:
    import simplejson as json

@task
def extract_file_info(file_id):
    """ This task uses python-neuroshare or NEO I/O to extract the information
    about the file with neurophysiological data. Saves a dict with the 
    extracted information to the Datafile object and an 'convertible' semaphor
    if the file is readable."""
    d = Datafile.objects.get(id=file_id) # may raise DoesNotExist
    try:
        f = ns.File(d.raw_file.path) # may raise IOerror / not able to read
        d.extracted_info = json.dumps(f._info)
        d.convertible = True # should check other f options?
    except (ArgumentError, DLLTypeUnknown, DLLNotFound):
        d.convertible = False
    d.save()
    return file_id


import tarfile
import zipfile
import os
import shutil
from django.core.files import File
from metadata.models import Section
from metadata.views import section_add
from settings import TMP_FILES_PATH

@task
def extract_from_archive(file_id):
    """ This task extracts files from the compressed file and creates 
    appropriate g-node datafile objects. For every extracted folder a g-node 
    section is created; all the files in the folder are linked to the related 
    section. The following file types are supported: zip, tar, gzip, bz2."""

    def create_section(new_name, where, parent_type="section"):
        tree_pos = 1
        sec_childs = where.section_set.all().order_by("-tree_position")
        if sec_childs:
            tree_pos = int(sec_childs.all()[0].tree_position) + 1
        if parent_type == "datafile": # link root section to original file
            parent_section = Section(title=new_name, parent_datafile=where,\
               tree_position=tree_pos)
        else: # create new section inside the parent section
            parent_section = Section(title=new_name, \
                parent_section=where, tree_position=tree_pos)
        parent_section.save()
        return parent_section

    def create_file(file_name, raw_file, parent_section):
        df = Datafile(title=file_name, owner=d.owner, raw_file=raw_file)
        df.save()
        if not parent_section:
            parent_section = create_section("root section", d, \
                "datafile")
        parent_section.addLinkedObject(df, "datafile")
        parent_section.save() # relate file to the section

    """ Algorithms for tar/zip look similar, but have major differences."""
    #if not TMP_FILES_PATH.endswith("/"): TMP_FILES_PATH += "/"
    d = Datafile.objects.get(id=file_id) # may raise DoesNotExist
    processed = False
    parent_section = None
    locations = {}
    if tarfile.is_tarfile(d.raw_file.path): # first read with tar
        cf = tarfile.open(d.raw_file.path) # compressed file
        for member in cf.getmembers():
            if member.isdir(): # create a section
                if member.name.endswith("/"): # because of python 2.5
                    name = member.name[:-1]
                else:
                    name = member.name
                try:
                    sec_name = name[name.rindex("/") + 1:]
                    parent_section = create_section(sec_name, \
                        locations[name[:name.rindex("/")]])
                except ValueError: # this is a 'root' folder
                    sec_name = name
                    parent_section = create_section(sec_name, d, "datafile")
                locations[name] = parent_section
            elif member.isfile(): # extract a file and to the section
                ef = cf.extractfile(member) # extracted file
                try:
                    file_name = member.name[member.name.rindex("/") + 1:]
                    parent_section = locations[member.name[:member.name.rindex("/")]]
                except ValueError: # this file is in the 'root' of archive
                    if not locations.has_key("/"):
                        locations["/"] = create_section("extracted", d, "datafile")
                    parent_section = locations["/"]
                    file_name = member.name
                create_file(file_name, File(ef), parent_section)
        processed = True
    elif zipfile.is_zipfile(d.raw_file.path): # or read with zip
        cf = zipfile.ZipFile(d.raw_file.path) # compressed file
        test = cf.infolist()[0].filename.split("/") # windows-made zips do not show the root folder
        if len(test) > 1:
            if len(test[1]) > 0:
                parent_section = create_section(test[0], d, "datafile")
                locations[test[0]] = parent_section
        for member in cf.infolist():
            if member.file_size == 0 and member.filename.endswith("/"): # is there a better way to detect folder?
                try:
                    sec_name = member.filename[member.filename[:-1].rindex("/") + 1:-1]
                    parent_section = create_section(sec_name, \
                        locations[member.filename[:member.filename[:-1].rindex("/")]])
                except ValueError: # this is a 'root' folder
                    sec_name = member.filename[:-1]
                    parent_section = create_section(sec_name, d, "datafile")
                locations[member.filename[:-1]] = parent_section
            else: # this should be a file
                tmpdirname = "%sportal_tmp_extraction_files_%s" % (TMP_FILES_PATH, d.id)
                os.makedirs(tmpdirname)
                try:
                    ef_path = cf.extract(member, tmpdirname) # extracted file
                except AttributeError: # stupid python 2.5 again
                    ef_path = tmpdirname + member.filename[member.filename.rindex("/") + 1:]
                    ef = open(ef_path, "w")
                    ef.write(cf.read(member.filename))
                    ef.close()
                try:
                    file_name = member.filename[member.filename.rindex("/") + 1:]
                    parent_section = locations[member.filename[:member.filename.rindex("/")]]
                except ValueError: # this file is in the 'root' of archive
                    if not locations.has_key("/"):
                        locations["/"] = create_section("root section", d, "datafile")
                    parent_section = locations["/"]
                    file_name = member.filename
                create_file(file_name, File(open(ef_path, "r")), parent_section)
                shutil.rmtree(tmpdirname) # clean temporary extracted file
        processed = True
    if processed: # indicate the file was processed
        d.extracted = "succeded"
        d.save()
    return file_id


"""
# UNDER DEVELOPMENT
import neuroshare as ns
from neo.core import * # import all NEO base classes

def convert_from_neuroshare(file_id, conv_seg=True):
    Converts data from the Neuroshare-compliant file to the native G-Node
    (NEO-like) format. The conversion is made in two steps:
    - first data is converted to pure NEO (https://neuralensemble.org/svn/neo/)
    - NEO objects are stored at G-Node. 
    d = Datafile.objects.get(id=file_id) # may raise DoesNotExist
    fd = ns.File(d.raw_file.path)
    segment = Segment() # we put all file contents in one segment
    for entity in fd.entities:
        if entity.entity_type == 1: # this is an EVENT ENTITY
            ea = EventArray(name=e.label)
            for e_id in range(entity.item_count):
                timestamp, data = entity.get_data(e_id)
                event = Event(time=timestamp, label=str(data))

            segment.eventarrays.append(ea)

"""

