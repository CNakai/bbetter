import click
import os
import shutil
import sys
import zipfile


@click.command()
@click.option('--extract_zips', is_flag=True, default=True, help=(
    "Indicates that any zipfiles in student submissionx should be unzipped "
    "in that student's submission directory.  Additionally, if the zipfile "
    "contains only a single directory then the contents of that directory are "
    "elevated to the level of that directory and then it is deleted."
))
@click.argument('submission_zipfile')
@click.argument('STUDENT_SUBMISSION_DIRECTORY')
def unpack(submission_zipfile, student_submission_directory, extract_zips):
    """The files of each student's submission are placed into a subdirectory
    within the STUDENT_SUBMISSION_DIRECTORY and the filename prefix added by
    BBLearn is removed from them.

    SUBMISSION_ZIPFILE: BBLearn assigment submission zip file

    STUDENT_SUBMISSION_DIRECTORY: Path for directory which will contain a
    subdirectory for each student's submission; the directory will be created
    if it does not exist

    """
    if not os.path.isfile(submission_zipfile):
        print("Whoops, it seems that there is no file at", submission_zipfile)
        sys.exit(1)

    extract_student_submissions_into_individual_directories(submission_zipfile, student_submission_directory)

    if extract_zips:
        extract_and_delete_and_normalize_submitted_zipfiles(student_submission_directory)

    print("\nSuccess")


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
        print(filename)
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
    front = filename.split(sep='_attempt_', maxsplit=2)[0]
    return front[front.rindex('_') + 1:]


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
    # TODO: Handle the BBLearn submission case better; rename it?  It currently
    # comes out as just a date.txt
    back = filename.split(sep='_attempt_', maxsplit=2)[1]
    return back[back.find('_') + 1:]


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
    singular_contents_directory_path = get_singular_contents_directory_path(path_to_extracted_contents)
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
