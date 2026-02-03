import os
import sys
import typing
import argparse
import collections
from dotenv import load_dotenv

from drive_functions import *

load_dotenv()

PATH_TO_BACKUP = os.getenv("BACKUP_PATH")
BACKUP_RELATIVE_PATH = r""
BACKUP_SERIAL_NUMBER = int(os.getenv("BACKUP_DRIVE_SERIAL"))
COMPARE = lambda x, y: collections.Counter(x) == collections.Counter(y)

class ExpectedFlags(typing.TypedDict):
    filepath_to_backup: typing.Union[str | pathlib.Path]
    relativepath: typing.Union[str | pathlib.Path]
    serial: int
    dryrun: bool
    verbose: bool
    getmountpoint: bool
    yes: bool

def get_flags(*, parse_flags: bool = True, flags_dict: dict = {}) -> dict:
    """
    Docstring for get_flags
    
    :param parse_flags: Read flags passed into file
    :type parse_flags: bool
    :param flags_dict: Contains arguments if parse_flags is False
    :type flags_dict: dict
    :return: Dictionary for flags
    :rtype: dict
    """
    if not parse_flags:
        if not COMPARE(flags_dict.keys(), ExpectedFlags.__mutable_keys__):
            raise ValueError(f"Expected: {(ExpectedFlags.__mutable_keys__)}, Got: {list(flags_dict.keys())}")
        else:
            return flags_dict

    parser = argparse.ArgumentParser(
        prog= "File backup",
        description="Backs up files into external drive",
        add_help=True
    )
    parser.add_argument('filepath_to_backup', nargs='?', type=str, default=PATH_TO_BACKUP, help="Absolute path of folder / file to backup") # nargs: optional input
    parser.add_argument('-sn', '--serial', type=int, default=BACKUP_SERIAL_NUMBER, help="Serial number of drive")
    parser.add_argument('-p', '--relativepath', type=str, default=BACKUP_RELATIVE_PATH, help="Relative path to backup files, default: ''")
    parser.add_argument('-dr', '--dryrun', action='store_true', help="Visualize changes before its made")
    parser.add_argument('-v', '--verbose', action='store_true') # False by default
    parser.add_argument('-mp', '--getmountpoint', action='store_true', help="Get list of serial numbers for drives") # False by default
    parser.add_argument('-y', '--yes', action='store_true', help="Start backup without user input") # False by default
    args = parser.parse_args()
    
    if args.getmountpoint:
        check_drives(-1, True)
        sys.exit(0)  # Exit after showing drives

    return args.__dict__

def main():
    # {"filepath_to_backup": "yes", "serial": 1, "relativepath": "yes", "dryrun": False, "verbose": False, "getmountpoint": False}
    args_value = get_flags()
    drive_letter, volume_name = check_drives(args_value["serial"])
    if drive_letter is None:
        print("No drive detected. Exiting...")
        sys.exit(0)

    print('\033[93m' + 
              f"Backing up {args_value['filepath_to_backup']} to drive {drive_letter}({volume_name}) with flags --verbose={args_value["verbose"]} and --dryrun={args_value["dryrun"]}"
              + '\033[0m')
    if not args_value["dryrun"] and not args_value["yes"]:
        user_input = input("Start backup? [y/n]: ")
        if user_input == '' or user_input[0].lower() != 'y':
            print("Aborting...")
            sys.exit(1)
    if args_value["dryrun"]:
        args_value["verbose"] = True
        
    backup_files(args_value["serial"], args_value["relativepath"], args_value["filepath_to_backup"], args_value["verbose"], args_value["dryrun"])

if __name__ == "__main__":
    main()