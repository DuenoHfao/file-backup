import os, pathlib, shutil
import typing
import win32api

from hashes import *

def check_drives(
        attached_drive_serial_number: int, 
        print_all_drives: bool = False
    ) -> typing.Tuple[typing.Union[str|None], typing.Union[str|None]]:
    """
    Docstring for check_drives
    
    :param attached_drive_serial_number: Serial number of backup drive
    :type attached_drive_serial_number: int
    :param print_all_drives: Debug: find serial number of all existing drives
    :type print_all_drives: bool
    :return: Drive letter and volume name of drive corresponding to serial number
    :rtype: Tuple[str | None, str | None]
    """
    drive_list = filter(
        lambda x: x != "", win32api.GetLogicalDriveStrings().split('\x00')
        )
    
    for drive_letter in drive_list:
        volume_name, serial_num, _, _, _ = win32api.GetVolumeInformation(drive_letter)
        if print_all_drives:
            print(f"Drive letter: {drive_letter.ljust(10, ' ')} Volume name: {volume_name.ljust(20, ' ')} Serial number: {str(serial_num).ljust(10, ' ')}")
            continue
        if serial_num == attached_drive_serial_number:
            return drive_letter, volume_name

    return None, None

def backup_files(
        attached_drive_serial_number: int,
        backup_relative_path: str,
        path_to_backup: str,
        verbose: bool = False,
        dryrun: bool = False
    ) -> None:
    
    drive_letter, volume_name = check_drives(attached_drive_serial_number)

    if drive_letter is None:
        exit()

    win32api.MessageBox(0, 'BACKUP IS STARTING', 'NOTICE!')
    new_path = os.path.join(drive_letter, (pathlib.Path(backup_relative_path) if backup_relative_path != "" else ""), os.path.basename(path_to_backup))
    print(f"Copying {path_to_backup} -> {new_path}")

    for (root, _, filenames) in os.walk(path_to_backup):
        for file in filenames:
            original_filepath = os.path.join(root, file)
            relative_filepath = original_filepath[len(path_to_backup)+1:]
            backup_filepath = os.path.join(new_path, relative_filepath)
            
            if verbose:
                print(f"Comparing {original_filepath} -> {backup_filepath}")

            if os.path.exists(original_filepath) and os.path.exists(backup_filepath):
                files_equal = compare_file_hashes(original_filepath, backup_filepath)
                if files_equal:
                    continue
            
            files_equal = False
            match os.path.exists(backup_filepath):
                case False:
                    if verbose:
                        print(f"Making directory: {os.path.dirname(backup_filepath)}")
                        
                    if not dryrun:
                        os.makedirs(os.path.dirname(backup_filepath), exist_ok=True)
                    
                case True:
                    ctr = 1
                    while True:
                        backup_filepath_title, ext = os.path.splitext(backup_filepath)
                        new_backup_filepath = backup_filepath_title + f"_v{ctr}" + ext
                        if verbose:
                            print(f"New backup location: {new_backup_filepath}")

                        if not os.path.exists(new_backup_filepath):
                            backup_filepath = new_backup_filepath
                            break
                        if compare_file_hashes(original_filepath, new_backup_filepath):
                            if verbose:
                                print("File hashes equal")
                            files_equal = True
                            break
                        ctr += 1
            
            if files_equal:
                continue

            if verbose:
                print(f"{original_filepath} -> {backup_filepath}")

            if not dryrun:
                shutil.copy2(original_filepath, backup_filepath)
            
    win32api.MessageBox(0, 'Backup is completed', 'NOTICE!')