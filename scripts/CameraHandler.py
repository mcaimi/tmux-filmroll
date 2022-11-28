#!/usr/bin/env python
#
# RAW Import and Sort Utility
#

import os
import sys
import shutil
from argparse import ArgumentParser
from datetime import datetime

# for GObject Introspection
import gi

# open GExiv2 library via GObject Introspection
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

RAW_TYPES = [
        ".arw", # SONY
        ".nef", # NIKON
        ".cr2", # CANON
        ".raf", # FUJIFILM
        ".orf", # OLYMPUS
        ".dng"  # LEICA - DIGITAL NEGATIVE
        ]

# Image Wrapper Class
class ImageObject(object):
    # object constructor
    def __init__(self, source_filename=None, destination_path=None):
        self.final_path = None
        self.image_filename = source_filename
        self.destination_path = destination_path
        self.exifparser = GExiv2.Metadata()
        try:
            if self.image_filename != None:
                self.open()
        except Exception as e:
            raise e

    # Open image
    def open(self):
        self.exifparser.open_path(self.image_filename)

    # return the date on which this picture has been taken in (y,m,d) format
    def time_info(self):
        try:
            self.picture_taken = self.exifparser.get_date_time()
            year, month, day = self.picture_taken.year, self.picture_taken.month, self.picture_taken.day
        except KeyError as e: # no EXIF metadata found... need to check file timestamp
            tstamp = datetime.fromtimestamp(os.stat(self.image_filename).st_mtime)
            year, month, day = tstamp.year, tstamp.month, tstamp.day

        return (year, month, day)

    # build destpath
    def _dest_path(self):
        if (self.destination_path[-1] != "/"):
            self.destination_path += "/"

        return r"%s/%s/%s/%s/" % (self.destination_path, *self.time_info())

    # get source filename
    def base_filename(self):
        return os.path.split(self.image_filename)[1]

    # assert that destination path is present on the filesystem
    # create path if necessary
    def prepare_destination_path(self, modifier=None):
        if modifier is None:
            dpath = self._dest_path()
        else:
            dpath = self._dest_path() + modifier

        if not os.path.exists(dpath):
            print("\t->Need to create directory: %s" % dpath)
            os.makedirs(dpath)

        dpath = os.path.normpath(dpath)

        if dpath[-1] != "/":
            self.final_path = dpath + "/"
        else:
            self.final_path = dpath

    # transfer file to destination
    def transfer(self):
        filename = self.base_filename()
        if os.path.exists(self.final_path + filename):
            print("\t--> Skipping existing file %s..." % (self.final_path + filename))
        else:
            print("=| Importing [%s] to [%s]..." % (self.image_filename, self.final_path))
            shutil.copy2(self.image_filename, self.final_path)

# Camera Importer Class
class CameraImport():
    def __init__(self, source_path, destination_path, extensions=RAW_TYPES):
        self.num_jpegs = 0
        self.num_raws = 0

        self.source_path = source_path
        self.destination_path = destination_path

        self.raw_ext = []
        if extensions != None:
            for ext in extensions:
                if not(ext in self.raw_ext):
                    self.raw_ext.append(ext.upper())

        if not os.path.exists(self.destination_path):
            os.makedirs(self.destination_path)

    def assert_path_ok(self):
        return not (self.source_path == self.destination_path)

    def init_file_lists(self):
        self.filelist = [ topdir + os.sep + fname\
                        for topdir, innerdirs, filelist in os.walk(self.source_path)\
                        for fname in filelist ]

        if len(self.raw_ext) > 0:
            self.raw_list = []
            for rawtype in self.raw_ext:
                self.raw_list += list(filter(lambda x: os.path.splitext(x)[1].upper() == rawtype.upper(), self.filelist))

        self.jpeg_list = list(filter(lambda x: os.path.splitext(x)[1].upper() == ".jpg".upper(), self.filelist))

        self.num_jpegs = len(self.jpeg_list)
        self.num_raws = len(self.raw_list)

    def n_raws():
        return self.num_raws

    def n_jpegs():
        return self.num_jpegs

    def transfer_jpegs(self):
        for jpeg in self.jpeg_list:
            # Instantiate new ImageOp Object
            next_file = ImageObject(source_filename=jpeg, destination_path=self.destination_path)
            next_file.prepare_destination_path(modifier="/jpg/")

            # copy file to destination!
            next_file.transfer()

            print("")

    def transfer_raws(self):
        for raw in self.raw_list:
            # instantiate imageop object
            next_file = ImageObject(source_filename=raw, destination_path=self.destination_path)
            next_file.prepare_destination_path(modifier="/raw/")

            # copy to destination
            next_file.transfer()

            print("")

# main
if __name__ == "__main__":
    ap = ArgumentParser(prog="CameraImport", description="RAW and JPEG import utility")
    ap.add_argument("--count", action='store_true', help="Count the number of files to import and report this info.")
    ap.add_argument("--source", help="Source path from which we will copy files.")
    ap.add_argument("--destination", help="Destiantion path to which we will copy files.")
    # parse command line
    opts = ap.parse_args()
    source = opts.source
    destination = opts.destination

    if source is None or destination is None:
        print("Syntax Error")
        sys.exit(-1)

    if opts.count is True:
        ch = CameraImport(source_path=source, destination_path=destination)
        ch.init_file_lists()
        print("Need to import [%s] JPEG files and [%s] RAW files. Continue?" % (ch.num_jpegs, ch.num_raws))
    else:
        print("Transferring from %s to %s...." % (source, destination))
        ch = CameraImport(source_path=source, destination_path=destination)
        ch.init_file_lists()
        # start transferring jpegs
        ch.transfer_jpegs()
        # start transferring raws
        ch.transfer_raws()
        # done

    sys.exit(0)
