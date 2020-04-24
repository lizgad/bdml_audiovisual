import argparse
import os

from scripts.config import load_bdml_config
from scripts.config import load_project_config
from scripts.filesystem import copy_files
from scripts.helpers import extract_metadata_from_export
from scripts.helpers import filemaker_namespace
from scripts.parse_logs import parse_logs
from scripts.make_bdml_upload_xml import make_bdml_upload_xml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")


class BDMLMetadataPrep(object):
    def __init__(self, project_name, ignore_existing=False, force_copy=False, skip_copy=False):
        self.project_name = project_name
        self.project_dir = os.path.join(PROJECTS_DIR, project_name)
        bdml_config_file = os.path.join(BASE_DIR, "bdml_config.cfg")
        default_config_file = os.path.join(BASE_DIR, "default_config.cfg")
        self.bdml_config = load_bdml_config(bdml_config_file)
        self.project_config = load_project_config(self, default_config_file)
        self.fmpro_nsmap = filemaker_namespace()
        self.ignore_existing = ignore_existing
        self.force_copy = force_copy
        self.skip_copy = skip_copy

    def make_upload_xml(self):
        metadata = extract_metadata_from_export(self)
        files_not_found = copy_files(self, metadata)
        make_bdml_upload_xml(self)
        if len(files_not_found) > 0:
            print("***** {} FILES NOT FOUND *****".format(len(files_not_found)))
            print("\n".join(files_not_found))

    def parse_logs(self):
        parse_logs(self)


def main():
    parser = argparse.ArgumentParser(description='Make XML to upload to the BDML')
    parser.add_argument('name',
                        choices=os.listdir(PROJECTS_DIR),
                        help='Enter the project name')
    parser.add_argument('-l', '--logs', action="store_true", help="Parse logs")
    parser.add_argument('-i', '--ignoreexisting', action="store_true", help="Ignore (do not copy) files if they exist in upload directory")
    parser.add_argument('-f', '--forcecopy', action="store_true", help="Copy files even if they already exist in upload directory")
    parser.add_argument('-s', '--skipcopy', action="store_true", help="Skip copying files")
    args = parser.parse_args()
    project_name = args.name
    BDMLMetadataPrepper = BDMLMetadataPrep(project_name, ignore_existing=args.ignoreexisting, force_copy=args.forcecopy, skip_copy=args.skipcopy)
    if args.logs:
        BDMLMetadataPrepper.parse_logs()
    else:
        BDMLMetadataPrepper.make_upload_xml()


if __name__ == "__main__":
    main()
