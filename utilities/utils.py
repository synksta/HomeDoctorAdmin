import os
import json


# Returns total size of files in the directory [bytes]
def get_dir_size(path):
    total_size = 0
    with os.scandir(path) as scanned_path:
        for dir in scanned_path:
            if dir.is_file(follow_symlinks=False):
                total_size += dir.stat(follow_symlinks=False).st_size
    return total_size


def get_sorted_list_of_files_by_date(path):
    result = []
    if os.path.exists(path):
        result = sorted(
            list(
                filter(
                    os.path.isfile,
                    list(map(lambda n: os.path.join(path, n), os.listdir(path))),
                )
            ),
            key=os.path.getmtime,
        )
    return result


def correct_file_extension(file_name: str, extension: str):

    file_name = list(filter(lambda word: len(word) > 0, file_name.split(".")))[0]
    extension = extension.replace(".", "")

    file_name = file_name.replace(extension, "")
    file_name += f".{extension}"

    return file_name


def sync_dict_with_json(dictionary, file_name, root_dir="./"):

    file_name = correct_file_extension(file_name, "json")

    write = not os.path.exists(f"{root_dir}{file_name}")
    print(f"write: {write}")
    if not write:
        with open(f"{root_dir}{file_name}", "r") as settings_file:
            user_settings: dict = json.load(settings_file)
            for key in list(dictionary.keys()):
                if key in user_settings:
                    dictionary[key] = user_settings[key]
            write = len(list(user_settings.keys())) != (list(dictionary.keys()))
    if write:
        with open(f"{root_dir}{file_name}", "w") as settings_file:
            settings_file.write(
                json.dumps(obj=dictionary, indent=len(dictionary), ensure_ascii=False)
            )

    return dictionary
