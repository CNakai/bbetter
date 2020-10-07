import argparse
import click
import os
import shutil
import subprocess
import sys
import zipfile


@click.command()
def unpack():
    """This program extracts student submissions from a BBLearn zip file into their
    own directory and removes the BBLearn prefix from their filenames.
    Optionally, it can also unzip any zipfiles in the students' submissions

    """
    print('money')


def main():
    args = create_parser().parse_args()
    zipfile_path = args.zipfile_path
    top_level_student_directory_path = args.student_directory_path

    if not os.path.isfile(zipfile_path):
        print("Whoops, it seems that there is no file at", zipfile_path)
        sys.exit(1)

    extract_student_submissions_into_individual_directories(zipfile_path, top_level_student_directory_path)

    if args.extract_submitted_zips:
        extract_and_delete_and_normalize_submitted_zipfiles(top_level_student_directory_path)

    print("\nSuccess")


def create_parser():
    description = "This program extracts student submissions from a BBLearn zip file into their own " + \
        "directory and removes the BBLearn prefix from their filenames.\n" + \
        "Optionally, it can also:\n" + \
        "\t+ Copy provided files into each created student directory\n" + \
        "\t+ Unzip any zipfiles in the students' submissions\n"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('zipfile_path',
                        help='Path to BBLearn submission zip file')

    parser.add_argument('student_directory_path',
                        help='Path to directory where student subdirectories will be created')

    parser.add_argument('-e', '--extract-submitted-zips', dest='extract_submitted_zips',
                        help='Indicates that any zipfiles in a student submission should be unzipped in ' + \
                        'that student\'s submission directory.  Additionally, if the only thing in the ' + \
                        'zipfile is a single directory, the contents of that directory are elevated to ' + \
                        'the level of that directory and then it is deleted.')
    return parser


def extract_student_submissions_into_individual_directories(zipfile_path, top_level_submission_directory_path):
    create_top_level_submission_directory(top_level_submission_directory_path)
    unzip_submission_files_into_directory(zipfile_path, top_level_submission_directory_path)
    student_ids = get_student_ids_from_submission_filenames(top_level_submission_directory_path)
    id_to_filename_map = create_student_id_to_submission_filename_map(student_ids, top_level_submission_directory_path)
    relocate_submission_files_to_per_student_directories(top_level_submission_directory_path, id_to_filename_map)


def create_top_level_submission_directory(directory_path):
    print("Creating directory for containing student submissions...")
    try:
        os.mkdir(directory_path)
    except FileExistsError as e:
        if not os.listdir(directory_path) == []: # Check if directory is empty
            should_continue = prompt_user_for_directory_clearing(directory_path)
            if not should_continue:
                print("Quitting...")
                sys.exit(0)
            clear_directory(directory_path)


def prompt_user_for_directory_clearing(student_submission_directory_path):
        print("Proposed directory for containing student submissions already exists and is not empty!")
        print("\nTo continue all files in this directory must be DELETED!")
        response = input("Do you want to continue? Y/n: ").lower()
        return response in {'yes', 'ye', 'y', ''}


def clear_directory(directory_path):
    print("Clearing directory...")
    shutil.rmtree(directory_path)
    os.mkdir(directory_path)
    print("Done!")
    

def unzip_submission_files_into_directory(zipfile_path, destination_directory_path):
    print("\nUnzipping assignment archive...")
    the_zip = zipfile.ZipFile(zipfile_path)
    the_zip.extractall(destination_directory_path)
    print("Done!")


def get_student_ids_from_submission_filenames(submission_files_path):
    student_ids = set()
    for filename in sorted(os.listdir(submission_files_path)):
        student_ids.add(get_student_id_from_filename(filename))
    return student_ids


def create_student_id_to_submission_filename_map(student_ids, submission_files_path_path):
    id_to_filename_map = {}
    for id in student_ids:
        id_to_filename_map[id] = []

    for filename in sorted(os.listdir(submission_files_path_path)):
        id_to_filename_map[get_student_id_from_filename(filename)].append(filename)

    return id_to_filename_map


def get_student_id_from_filename(filename):
    return filename.split(sep='_', maxsplit=2)[1]


def relocate_submission_files_to_per_student_directories(submission_files_path, id_to_filename_map):
    print("\nRelocating files to student directories...")
    for id in id_to_filename_map:
        student_directory_path = create_student_directory(submission_files_path, id)
        for filename in id_to_filename_map[id]:
            old_file_path = os.path.join(submission_files_path, filename)
            new_file_path = os.path.join(student_directory_path,
                                         remove_bblearn_filename_prefix(filename))
            print("\tmoving " + old_file_path)
            print("\tto " + new_file_path)
            os.rename(old_file_path, new_file_path)


def create_student_directory(submission_files_path, student_directory_name):
    print("\nCreating student directory " + student_directory_name)
    student_directory_path = os.path.join(submission_files_path, student_directory_name)
    os.mkdir(student_directory_path)
    return student_directory_path


def remove_bblearn_filename_prefix(filename):
    return filename.split(sep='_', maxsplit=4).pop()


def extract_and_delete_and_normalize_submitted_zipfiles(top_level_student_directory_path):
    for student_directory_name in os.listdir(top_level_student_directory_path):
        student_directory_path = os.path.join(top_level_student_directory_path, student_directory_name) 
        for item in os.listdir(student_directory_path):
            if '.zip' in item:
                zipfile_path = os.path.join(student_directory_path, item)
                zipfile.ZipFile(zipfile_path).extractall(student_directory_path)
                os.remove(zipfile_path)
                normalize(student_directory_path)
                break


def normalize(path_to_extracted_contents):
    shutil.rmtree(os.path.join(path_to_extracted_contents, '__MACOSX'), ignore_errors=True)
    shutil.rmtree(os.path.join(path_to_extracted_contents, '.DS_store'), ignore_errors=True)
    singular_contents_directory_path = get_singular_contents_directory_path_(path_to_extracted_contents)
    if singular_contents_directory_path is not None:
        for real_contents_filename in os.listdir(singular_contents_directory_path):
            shutil.copy2(os.path.join(singular_contents_directory_path, real_contents_filename),
                         path_to_extracted_contents)
        shutil.rmtree(singular_contents_directory_path)


def get_singular_contents_directory_path(path_to_extracted_contents):
    contents_filenames = os.listdir(path_to_extracted_contents)
    if len(contents_filenames) == 1:
        contents_subfolder_path = os.path.join(path_to_extracted_contents, contents_filenames[0])
        if os.path.isdir(contents_subfolder_path):
            return contents_subfolder_path
    return None


if __name__ == "__main__":
    main()
