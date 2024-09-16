import os

def get_cache_folder() -> str:
    """ Get the path to the cache folder.
    Returns the path to the cache folder.
    """
    # this file is in "path_to_project/ja_implemental_dashboard/v_something/caching/caching.py"
    cache_folder = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "cache"))
    # create the folder if it does not exist
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    return cache_folder


