import os
import glob


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
