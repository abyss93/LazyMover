#!/usr/bin/python3

import argparse
import os
import os.path
import shutil
from datetime import datetime
from pathlib import Path
from time import strftime, localtime

from PIL import Image
from pillow_heif import register_heif_opener


def is_valid_image(file_name):
    try:
        with Image.open(file_name) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        print(f"\tNot an image or non valid image file: {file_name}")
        return False


def move_by_exif_datetime(f_abs_p, filename, destination, exif_datetime, dry_run):
    date_parsed = datetime.strptime(exif_datetime, "%Y:%m:%d %H:%M:%S").strftime('%Y/%m/%d').split("/")
    y = date_parsed[0]
    m = date_parsed[1]
    d = date_parsed[2]
    print(f"\t\tEXIF DateTime tag: {d}/{m}/{y}")
    path = Path(f"{destination}/{y}/{m}/{d}/")
    if not dry_run:
        # I create all the directory tree if it does not exist
        path.mkdir(parents=True, exist_ok=True)
        shutil.move(f_abs_p, f"{destination}/{y}/{m}/{d}/sorted_{filename}")
    else:
        print(f"\t\t[DRYRUN move to] {destination}/{y}/{m}/{d}/sorted_{filename}")


def move_by_file_stat(f_abs_p, filename, destination, dry_run):
    stat_modtime_split = strftime('%Y/%m/%d', localtime(os.path.getmtime(f_abs_p))).split("/")
    y = stat_modtime_split[0]
    m = stat_modtime_split[1]
    d = stat_modtime_split[2]
    print(f"\t\tModified stat date: {d}/{m}/{y}")
    path = Path(f"{destination}/{y}/{m}/{d}/")
    if not dry_run:
        # I create all the directory tree if it does not exist
        path.mkdir(parents=True, exist_ok=True)
        shutil.move(f_abs_p, f"{destination}/{y}/{m}/{d}/sorted_{filename}")
    else:
        print(f"\t\t[DRYRUN move to] {destination}/{y}/{m}/{d}/sorted_{filename}")


def image_sort(to_be_sorted, destination, dry_run):
    for root, dirs, files in os.walk(to_be_sorted, followlinks=False):
        print(f"Processing Dir: {root}")
        for fl in files:
            filename = str(fl)
            f_abs_p = f"{root}/{fl}"
            # check if file is really an image because I want to use EXIF info...
            if is_valid_image(f_abs_p):
                print(f"\tProcessing Image: {f_abs_p}")
                img = Image.open(f_abs_p)
                img_exif = img.getexif()
                if img_exif is None or img_exif == {}:
                    # no EXIF data, fallback...
                    move_by_file_stat(f_abs_p, filename, destination, dry_run)
                else:
                    # there are some EXIF tags
                    try:
                        img_exif = img_exif.items()
                        exif_date_found = False
                        for key, val in img_exif:
                            # EXIF tag DateTime = 0x0132 (306 base-10)
                            # the simplest EXIF date tag, keeping it simple
                            if key == 306:
                                exif_date_found = True
                                move_by_exif_datetime(f_abs_p, filename, destination, val, dry_run)
                            # here manage other "date" EXIF tags if needed....
                        if not exif_date_found:
                            # there are no tags I'm interested in, fallback...
                            move_by_file_stat(f_abs_p, filename, destination, dry_run)
                    except KeyError:
                        # not able to get tag data, fallback...
                        move_by_file_stat(f_abs_p, filename, destination, dry_run)
            else:
                # otherwise I move by file last modification time
                # other files, for example videos, go here
                # I suppose no other file types are in a media folder...
                # for iPhone the stat modification date is equal to the day the photo/video was taken
                print(f"\tProcessing non-image file: {f_abs_p}")
                move_by_file_stat(f_abs_p, filename, destination, dry_run)


if __name__ == "__main__":
    print("""
    __                      __  ___                    
   / /   ____ _____  __  __/  |/  /___ _   _____  _____
  / /   / __ `/_  / / / / / /|_/ / __ \ | / / _ \/ ___/
 / /___/ /_/ / / /_/ /_/ / /  / / /_/ / |/ /  __/ /    
/_____/\__,_/ /___/\__, /_/  /_/\____/|___/\___/_/     
                  /____/                               
    """)
    parser = argparse.ArgumentParser(description="""\033[35m -- LazyMover --\033[0m\n

    source_dir = root dir of media that you have to order ||
    dest_dir = root dir where sorted files will be MOVED ||
    
    Sort logic =
    each file is examined using EXIF DateTime tag, if that is not found it fallbacks to stat modification date (os.path.getmtime).
    Then the file is moved to destination directory dest_dir/year/month/day/sorted_<filename>
    """,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("source_dir", type=str, help="Source Directory")
    parser.add_argument("dest_dir", type=str, help="Destination Directory")
    parser.add_argument("-d", "--dry-run", help="Simulation of what would happen...", action="store_true",
                        default=False)
    args = parser.parse_args()
    parameters = vars(args)
    # I need this to be able to open iPhone .HEIF files
    register_heif_opener()
    # root path of the media to be sorted
    to_be_sorted = "/home/abyss/Pictures/iphone_photo"
    destination = "/home/abyss/Pictures"
    image_sort(args.source_dir, args.dest_dir, parameters["dry_run"])
