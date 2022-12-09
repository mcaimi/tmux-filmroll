#!/usr/bin/env python3
#
# RAW Import and Sort Utility
#

import os
import sys
import shutil
from argparse import ArgumentParser
from datetime import datetime
from typing import List, Tuple

# for GObject Introspection
import gi

# open GExiv2 library via GObject Introspection
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

RAW_TYPES: List = [
        ".arw", # SONY
        ".nef", # NIKON
        ".cr2", # CANON
        ".raf", # FUJIFILM
        ".orf", # OLYMPUS
        ".dng"  # LEICA - DIGITAL NEGATIVE
        ]

RASTER_TYPES: List = [
        ".jpg",
        ".jpeg",
        ".heif",
        ".heic",
        ".png",
        ".tga"
    ]

VIDEO_TYPES: List = [
        ".avi",
        ".mpg",
        ".mov",
        ".mkv"
    ]

# Image Wrapper Class
class ImageObject(object):
    # object constructor
    def __init__(self, source_filename: str, destination_path: str, dry_run: bool = False) -> None:
        self.final_path: str = None
        self.image_filename: str = source_filename
        self.destination_path: str = destination_path
        self.exifparser: GExiv2.Metadata = GExiv2.Metadata()
        self.dry_run = dry_run

        try:
            self.exifparser.open_path(self.image_filename)

            if self.exifparser.has_exif():
                try:
                    self.date_info: dict = self.exifparser.get_date_time()
                except KeyError: # EXIF metadata does not contain date/time info. fallback to file timestamp
                    self.date_info: dict = datetime.fromtimestamp(os.stat(self.image_filename).st_mtime)
            else:
                self.date_info: dict = datetime.fromtimestamp(os.stat(self.image_filename).st_mtime)

            self.exifparser.free()
        except Exception as e:
            raise e

    # build destpath
    def _dest_path(self) -> str:
        return f"{self.destination_path}/{self.date_info.year}/{self.date_info.month}/{self.date_info.day}/"

    # get source filename
    def base_filename(self) -> str:
        return os.path.split(self.image_filename)[1]

    # assert that destination path is present on the filesystem
    # create path if necessary
    def prepare_destination_path(self, modifier=None) -> None:
        if modifier is None:
            dpath = self._dest_path()
        else:
            dpath = f"{self._dest_path()}{modifier}"

        if not os.path.exists(dpath):
            print("\t->Need to create directory: %s" % dpath)
            if not self.dry_run:
                os.makedirs(dpath)

        dpath = os.path.normpath(dpath)

        if dpath[-1] != "/":
            self.final_path = f"{dpath}/"
        else:
            self.final_path = dpath

    # transfer file to destination
    def transfer(self) -> None:
        filename = self.base_filename()
        if os.path.exists(self.final_path + filename):
            print(f"\t--> Skipping existing file {self.final_path}{filename}...")
        else:
            print(f"=| Importing [{self.image_filename}] to [{self.final_path}]...")
            if not self.dry_run:
                shutil.copy2(self.image_filename, self.final_path)

# Camera Importer Class
class CameraImport():
    def __init__(self, source_path, destination_path, dry_run: bool = False) -> None:
        self.source_path: str = source_path
        self.destination_path: str = destination_path
        self.dry_run = dry_run

        self.raw_ext: List = [x.upper() for x in RAW_TYPES]
        self.raster_ext: List = [x.upper() for x in RASTER_TYPES]
        self.video_ext: List = [x.upper() for x in VIDEO_TYPES]

        if not os.path.exists(self.destination_path) and not self.dry_run:
            os.makedirs(self.destination_path)

    def assert_path_ok(self) -> bool:
        return not (self.source_path == self.destination_path)

    def init_file_lists(self) -> None:
        self.filelist = [ topdir + os.sep + fname\
                        for topdir, innerdirs, filelist in os.walk(self.source_path)\
                        for fname in filelist ]

        self.raw_list: List = []
        for rawtype in self.raw_ext:
            self.raw_list += list(filter(lambda x: os.path.splitext(x)[1].upper() == rawtype.upper(), self.filelist))

        self.raster_list: List = []
        for rastertype in self.raster_ext:
            self.raster_list += list(filter(lambda x: os.path.splitext(x)[1].upper() == rastertype.upper(), self.filelist))

        self.video_list: List = []
        for videotype in self.video_ext:
            self.video_list += list(filter(lambda x: os.path.splitext(x)[1].upper() == videotype.upper(), self.filelist))

        self.num_raws: int = len(self.raw_list)
        self.num_rasters: int = len(self.raster_list)
        self.num_video: int = len(self.video_list)

    def n_raws(self) -> int:
        return self.num_raws

    def n_rasters(self) -> int:
        return self.num_rasters

    def n_videos(self) -> int:
        return self.num_video

    def transfer_rasters(self) -> None:
        for raster in self.raster_list:
            # Instantiate new ImageOp Object
            next_file = ImageObject(source_filename=raster, destination_path=self.destination_path, dry_run=self.dry_run)
            next_file.prepare_destination_path(modifier="/rasters/")

            # copy file to destination!
            next_file.transfer()

            print("")

    def transfer_raws(self) -> None:
        for raw in self.raw_list:
            # instantiate imageop object
            next_file = ImageObject(source_filename=raw, destination_path=self.destination_path, dry_run=self.dry_run)
            next_file.prepare_destination_path(modifier="/raw/")

            # copy to destination
            next_file.transfer()

            print("")

    def transfer_videos(self) -> None:
        for video in self.video_list:
            # instantiate imageop object
            next_file = ImageObject(source_filename=video, destination_path=self.destination_path, dry_run=self.dry_run)
            next_file.prepare_destination_path(modifier="/video/")

            # copy to destination
            next_file.transfer()

            print("")

# main
if __name__ == "__main__":
    ap = ArgumentParser(prog="CameraImport", description="Image import utility")
    ap.add_argument("--count", action='store_true', help="Count the number of files to import and report this info.")
    ap.add_argument("--source", help="Source path from which we will copy files.")
    ap.add_argument("--destination", help="Destiantion path to which we will copy files.")
    ap.add_argument("--dryrun", action='store_true', help="Simulate run but do not actually copy or move files around.")

    # parse command line
    opts = ap.parse_args()
    source = opts.source
    destination = opts.destination

    if source is None or destination is None:
        print("Syntax Error")
        sys.exit(-1)

    if opts.count is True:
        ch = CameraImport(source_path=source, destination_path=destination, dry_run=opts.dryrun)
        ch.init_file_lists()
        print(f"Need to import [{ch.n_rasters()}] RASTER files, [{ch.n_raws()}] RAW files and [{ch.n_videos()}] Video files. Continue?")
    else:
        print(f"Transferring from {source} to {destination}....")
        ch = CameraImport(source_path=source, destination_path=destination, dry_run=opts.dryrun)
        ch.init_file_lists()
        # start transferring rasters
        ch.transfer_rasters()
        # start transferring raws
        ch.transfer_raws()
        # start transferring videos
        ch.transfer_videos()
        # done

    sys.exit(0)
