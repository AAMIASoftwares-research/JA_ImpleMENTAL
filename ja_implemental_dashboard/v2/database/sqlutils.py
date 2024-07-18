import os, sys, time, datetime
import pandas
import sqlite3

def convert_sas_datasets_to_sqlite3_db(files_folder: str, file_name_to_table_name_dict: dict[str:str], output_db_file: str, sas_file_ext:str=".sas7bdat"):
    """ Convert all the SAS7BDAT files in the folder to a single SQLite3 database file.
    The output database file is created if it does not exist, otherwise it is overwritten.
    The tables are named following the schema provided in the file_name_to_table_name_dict dictionary,
    composed as table_name : file_name (not whole path, with or without extension).
    The tables are created with the same column names as the SAS7BDAT files.
    """
    # create the empty database file
    if os.path.exists(output_db_file):
        os.remove(output_db_file)
    conn = sqlite3.connect(output_db_file)
    # fix files extensions
    for k, v in file_name_to_table_name_dict.items():
        if not v.endswith(sas_file_ext):
            f_without_ext = os.path.splitext(v)[0]
            file_name_to_table_name_dict[k] = f_without_ext + sas_file_ext
    # load the tables with pandas in chunks
    for table_name, file_name in file_name_to_table_name_dict.items():
        if "cohort" in table_name.lower():
            continue
        # keys are the new tables names, values the files names
        f = os.path.join(files_folder, file_name)
        if not os.path.exists(f):
            raise FileNotFoundError(f"{f}")
        print("Reading file: ", os.path.basename(f))
        with pandas.read_sas(f, chunksize=10000) as reader:
            for ic, chunk in enumerate(reader):
                print("Table:", table_name, "chunk", ic, "  |  DB size:", os.path.getsize(output_db_file) / 1024 / 1024, "MB               ", end="\r")
                # append the chunk to the table
                chunk.to_sql(table_name, conn, if_exists='append', index=False)
                conn.commit()
    # close the connection
    conn.close()
