import os
import hashlib
from .caching import get_cache_folder


def get_original_database_file_path_cache_file() -> str:
    """ Get the path to the cache file that contains the path to the original database file.
    Returns the path to the cache file.
    """
    cache_fname = "original_database_file.cache"
    cache_file = os.path.normpath(
        os.path.join(get_cache_folder(), cache_fname)
    )
    return cache_file

def get_original_database_file_path() -> str:
    """ Get the path to the original database file, which is saved in a cache file.
    Returns the path to the file.
    """
    cache_file = get_original_database_file_path_cache_file()
    if not os.path.exists(cache_file):
        return None
    with open(cache_file, "r") as f:
        path = f.read()
    if len(path) == 0:
        return None
    return str(path)

def get_original_database_hash_file_path() -> str:
    """ Get the path to the file that contains the hash of the original database file.
    Returns the path to the file.
    """
    fname = "db_hash_original.cache"
    path = os.path.normpath(
        os.path.join(get_cache_folder(), fname)
    )
    return path

def get_slim_database_hash_file_path() -> str:
    """ Get the path to the file that contains the hash of the slim database file.
    Returns the path to the file.
    """
    fname = "db_hash_slim.cache"
    path = os.path.normpath(
        os.path.join(get_cache_folder(), fname)
    )
    return path

def hash_database_file(file_path: str) -> str:
    """ Compute the hash of the database file.
    file_path: str
        The path to the database file.
    Returns the hash of the file.
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(1048576), b""):
            md5.update(byte_block)
    return md5.hexdigest()

def detect_original_database_has_changed() -> bool:
    """ Detect if the database file has changed since the last preprocessing.
    Returns True if the database file has changed, False otherwise.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        return True
    cache_file = get_original_database_hash_file_path()
    if not os.path.exists(cache_file):
        return True
    with open(cache_file, "r") as f:
        old_hash = f.read()
    database_file_hash = hash_database_file(get_original_database_file_path())
    return old_hash != database_file_hash

def get_slim_database_filepath() -> str:
    """ Get the path to the slim database file.
    Returns the path to the slim database file.
    """
    return os.path.normpath(
        os.path.join(
            os.path.dirname(get_original_database_file_path()),
            f"{os.path.basename(get_original_database_file_path()).replace('.sqlite3', '.jasqlite3')}"
        )
    )

def detect_slim_database_has_changed() -> bool:
    """ Detect if the slim database file has changed since the last preprocessing.
    Returns True if the slim database file has changed, False otherwise.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        return True
    cache_file = get_slim_database_hash_file_path()
    if not os.path.exists(cache_file):
        return True
    with open(cache_file, "r") as f:
        old_hash = f.read()
    slim_database_file = get_slim_database_filepath()
    if not os.path.exists(slim_database_file):
        return True
    slim_database_file_hash = hash_database_file(slim_database_file)
    return old_hash != slim_database_file_hash

def write_to_original_database_hash_file(hash_: str) -> None:
    """ Write the hash of the database file to a file in the cache folder.
    hash_: str
        The hash of the database file.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        os.makedirs(hash_folder)
    cache_file = get_original_database_hash_file_path()
    with open(cache_file, "w") as f:
        f.write(hash_)

def write_to_slim_database_hash_file(hash_: str) -> None:
    """ Write the hash of the slim database file to a file in the cache folder.
    hash_: str
        The hash of the slim database file.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        os.makedirs(hash_folder)
    cache_file = get_slim_database_hash_file_path()
    with open(cache_file, "w") as f:
        f.write(hash_)
