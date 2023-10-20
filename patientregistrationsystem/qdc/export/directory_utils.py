from os import path, makedirs


def create_directory(basedir: str, path_to_create: str) -> str:
    """
    Create a directory

    :param basedir: directory that already exists (parent path where new path must be included)
    :param path_to_create: directory to be created
    :return:
            - "" if path was correctly created or error message if there was an error
            - complete_path -> basedir + path created
    """

    complete_path = ""

    if not path.exists(basedir.encode("utf-8")):
        return "Base path does not exist", complete_path

    complete_path = path.join(basedir, path_to_create)

    # print("encode: ", sys.getfilesystemencoding(), sys.getdefaultencoding())
    # print("create_directory-encode:", complete_path.encode('utf-8'))
    if not path.exists(complete_path.encode("utf-8")):
        # print("create_directory:", basedir, path_to_create)
        # print("create_directory:", complete_path)
        makedirs(complete_path.encode("utf-8"))

    return "", complete_path
