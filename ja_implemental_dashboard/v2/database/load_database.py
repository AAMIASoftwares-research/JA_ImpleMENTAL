"""Use this module only once in the program as: from load_database import DB.

Other database utilities are available in the 'database' module.
"""
import os, time
import sqlite3

from .database import (
    standardize_table_names,
    check_database_has_tables,
    slim_down_database,
    preprocess_database_data_types,
    create_indices_on_ja_database,
    preprocess_database_datetimes,
    add_cohorts_table,
    make_age_startification_tables,
    get_all_years_of_inclusion,
)
from ..caching.database import (
    get_cache_folder,
)


# This file contains the script to load
# and preprocess the database.
# This file is to be imported only once by the dispatcher
# to import the connection to the database: DB
# from load_database import DB


#######################################################
# ***   MAIN LOGIC   ***
# - USER SELECTION OF THE DATABASE
# - CREATION/CONNECTION TO INTERNAL DATABASE
# - PREPROCESSING OF INTERNAL DATABASE
# - CREATION OF cohorts AND age_stratifications TABLES
#######################################################

# USER SELECTION OF THE DATABASE
print("Please select the database file using the file selection dialog that opened.")
import tkinter
from tkinter import filedialog
root = tkinter.Tk()
root.withdraw()
filedialog_cache_file = os.path.join(get_cache_folder(), "filedialog_last_used_directory.cache")
if os.path.exists(filedialog_cache_file):
    with open(filedialog_cache_file, "r") as f:
        last_used_dir = f.read()
else:
    last_used_dir = ""
if not os.path.exists(last_used_dir):
    last_used_dir = os.path.expanduser("~")
file_path = filedialog.askopenfilename(
    defaultextension=".sqlite3", 
    filetypes=[("SQLite3 database files", "*.sqlite3")],
    initialdir=last_used_dir,
)
if file_path == "":
    print("No file selected. Exiting.")
    exit()

# CONNECT TO USER SELECTED DATABASE
USER_DATABASE_FILE = os.path.normpath(file_path)
with open(filedialog_cache_file, "w") as f:
    f.write(os.path.dirname(USER_DATABASE_FILE))
del root, filedialog_cache_file, last_used_dir, file_path
DB = sqlite3.connect(USER_DATABASE_FILE)
# save original database file path into a cache file
from ..caching.database import get_original_database_file_path_cache_file
with open(get_original_database_file_path_cache_file(), "w") as f:
    f.write(USER_DATABASE_FILE)
    

# CREATION/CONNECTION TO INTERNAL DATABASE
_t0 = time.time()
# Standardize tables names
standardize_table_names(DB)
# Check if the database has the necessary tables
is_ok, missing = check_database_has_tables(DB)
if not is_ok:
    raise ValueError("The database is missing the following tables which are required:", missing)
# Preprocess the database: create a second database file (that will be used for the dashboard)
#                          containing only patients
#                          that are mental health patients of some sort, to exclude
#                          every other medical condition not of interest of the dashboard
new_db_path, _has_been_slimmed = slim_down_database(DB)
DB.close()
DB = sqlite3.connect(new_db_path)

# PREPROCESSING OF INTERNAL DATABASE
# Fix data types
preprocess_database_data_types(DB, force=_has_been_slimmed)
# Create indices on the tables
create_indices_on_ja_database(DB, force=_has_been_slimmed)
# Fix datetime columns
preprocess_database_datetimes(DB, force=_has_been_slimmed)

# CREATE THE 'cohorts' TABLE
add_cohorts_table(DB, force=_has_been_slimmed)

# CREATE THE 'age_stratification' TABLE
from ..indicator.widget import AGE_WIDGET_INTERVALS
_years_of_inclusion = get_all_years_of_inclusion(DB)
_age_stratifications_list = [v for v in AGE_WIDGET_INTERVALS.values()]
make_age_startification_tables(DB, _years_of_inclusion, _age_stratifications_list, force=_has_been_slimmed)

# CREATE INDICATOR CACHE DATABASE
from ..caching.indicators import initialize_indicators_cache_database
initialize_indicators_cache_database(force=_has_been_slimmed)

# PRINT OUT HOW MUCH IT TOOK
_t1 = time.time()
_dt = _t1 - _t0
hours = _dt//3600
minutes = (_dt//60)%60
seconds = _dt%60
print(f"Database checked and loaded in {hours:.0f}h {minutes:.0f}m {seconds:.0f}s")

# CLEAN MEMORY FROM USELESS VARIABLES
del _t0, _t1, _dt, hours, minutes, seconds, _years_of_inclusion, _age_stratifications_list 

# By the end of this script, what should be imported from this file
# is only the DB variable, which is the connection to the database.

