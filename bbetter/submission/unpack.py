import click
import shutil
import sys
import bbetter.submission.util as util
from os import listdir, mkdir, remove, rename, scandir
from os.path import isdir, exists, join
from zipfile import is_zipfile, ZipFile


@click.command()
@click.argument('submission_zip')
@click.argument('submission_dir')
@click.option('--extract_submitted_zips', is_flag=True, default=True, help=(
    """Unzip any zipfiles in student submissions and delete the zipfiles.

    Defaults to True."""
))
@click.option('--hoist_lone_subdirs', is_flag=True, default=True, help=(
    """If the only contents of a student's submission directory is a single
    subdirectory, then that subdirectory's contents are moved into the
    student's submission directory and the subdirectory is deleted also.  This
    takes place after extracting submitted zipfiles.

    Defaults to True."""
))
@click.option('--clean_up_student_dirs', is_flag=True, default=True, help=(
    """Deletes various extraneous files and directories that may be present in
    the student's submission directories.  This takes place after extracting
    submitted zips and hoisting lone subdirectories.

    Currently deletes the following files and directories:
        __MACOSX
        .DS_store

    Defaults to True."""
))
def unpack(submission_zip, submission_dir, extract_submitted_zips,
           hoist_lone_subdirs, clean_up_student_dirs):
    """The BBLearn assignment submission zipfile indicated by SUBMISSION_ZIP is
    unzipped at the SUBMISSION_DIR.  If no directory exists at that path, it
    will be created if it does not exist.  If it exists but is not empty, the
    user will be invited to remove its contents or quit.

    Once the submission directory has been prepared, the files from the
    submission zip are relocated to a subdirectory of the submission directory
    whose name is the student id of the student that submitted the file.  When
    the files are relocated, they are also renamed to remove the prefix added
    to the filename by BBLearn.

    """
    if not is_zipfile(submission_zip):
        print(f"Whoops, it seems that there is no zipfile at {submission_zip}")
        sys.exit(1)

    setup(submission_dir)

    print("\nUnzipping submission archive...")
    with ZipFile(submission_zip) as z:
        z.extractall(submission_dir)
        print("Done!")

    refile_per_student(submission_dir)

    for student_directory_entry in scandir(submission_dir):
        if extract_submitted_zips:
            extract_any_zips(student_directory_entry.path)
        if hoist_lone_subdirs:
            hoist_lone_subdir_if_exists(student_directory_entry.path)
        if clean_up_student_dirs:
            clean_up(student_directory_entry.path, extract_submitted_zips)

    print("\nSuccess")


def setup(submission_directory):
    """Ensures that submission_dir exists and is empty"""
    if isdir(submission_directory) and len(listdir(submission_directory)) == 0:
        pass  # Nothing to do
    elif not exists(submission_directory):
        print("Creating submission directory...")
        mkdir(submission_directory)
    else:
        print(f"{submission_directory} is not empty!")
        print("\nTo continue all files in this directory must be DELETED!")
        response = input("Do you want to continue? Y/n: ").lower()

        if response in ('yes', 'ye', 'y', ''):
            shutil.rmtree(submission_directory)
            mkdir(submission_directory)
        else:
            print("Quitting...")
            sys.exit(0)


def refile_per_student(submission_directory):
    """Creates per student subdirectories within the submission_dir and moves
    each students files into their directory"""
    submission_file_entries = sorted(
        list(scandir(submission_directory)),
        key=lambda entry: util.extract_student_id(entry.name)
    )

    print("\nRelocating files to student directories...")
    for entry in submission_file_entries:
        id = util.extract_student_id(entry.name)
        student_directory = join(submission_directory, id)

        if not exists(student_directory):
            print(f"\nCreating student directory {student_directory}")
            mkdir(student_directory)

        new_path = join(student_directory,
                        util.remove_bblearn_prefix(entry.name))
        print(f"\trenaming {entry.path}")
        print(f"\tto {new_path}")
        rename(entry.path, new_path)


def extract_any_zips(directory):
    "Extracts any zip files in the directory into the directory"
    for entry in scandir(directory):
        if is_zipfile(entry.path):
            with ZipFile(entry.path) as z:
                z.extractall(directory)


def hoist_lone_subdir_if_exists(directory):
    entries = list(scandir(directory))
    if len(entries) == 1 and entries[0].isdir():
        util.hoist_directory(entries[0].path)


def clean_up(student_directory, remove_zips=False):
    for cruft in ['__MACOSX', '.DS_store']:
        shutil.rmtree(join(student_directory, cruft), ignore_errors=True)

    if remove_zips:
        for file_entry in scandir(student_directory):
            if is_zipfile(file_entry.path):
                remove(file_entry.path)
