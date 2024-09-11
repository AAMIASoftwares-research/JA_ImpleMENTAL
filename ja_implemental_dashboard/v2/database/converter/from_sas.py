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


# load the tables in the mysql database (create the tables if they do not exist)
if __name__ == "__main__":
    # - connect to the database to load all example tables in it
    FILES_FOLDER = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia"
    DATABASE_FILENAMES_DICT = {
        "demographics": "demographics.sas7bdat",
        "diagnoses": "diagnoses.sas7bdat",
        "interventions": "interventions.sas7bdat",
        "pharma": "pharma.sas7bdat",
        "physical_exams": "physical_exams.sas7bdat"
    }
    database_file = "DATABASE.original_from_sas.mod.sqlite3"
    database_file = os.path.normpath(
        os.path.join(FILES_FOLDER, database_file)
    )
    if 1:
        convert_sas_datasets_to_sqlite3_db(
            files_folder=FILES_FOLDER,
            file_name_to_table_name_dict=DATABASE_FILENAMES_DICT,
            output_db_file=database_file
        )
    if 1:
        print("TEMPORARY: IF THIS APPEARS GO INTO SOURCE CODE AND PUT 'if 0' on line 57 or close to it.")
        db_sicilia_orig = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia\\DATABASE.original_from_sas.mod.sqlite3"
        db = sqlite3.connect(db_sicilia_orig)
        # goal: alter the demographics table to replace the EDU_LEVEL intervals from a TEXT based code
        #       to a numerical one, which are the ISCED levels from 0 to 8.
        #       Original educational levels are:
        #       - Null or None -> ISCED 9 (no educational level)
        #       - "0-5" -> ISCED 1 (primary education)
        #       - "6-8" -> ISCED 2 (lower secondary education)
        #       - "9-13" -> ISCED 3 (upper secondary education)
        #       - ">=14" -> ISCED 5 (after upper secondary education, could be 4, 6, 7, or 8)
        cursor = db.cursor()
        # how to alter values in a column
        # cursor.execute("UPDATE demographics SET EDU_LEVEL = '9-13' WHERE EDU_LEVEL = '6-8'")
        cursor.execute("UPDATE demographics SET EDU_LEVEL = '1' WHERE EDU_LEVEL LIKE '%0-5%'")
        cursor.execute("UPDATE demographics SET EDU_LEVEL = '2' WHERE EDU_LEVEL LIKE '%6-8%'")
        cursor.execute("UPDATE demographics SET EDU_LEVEL = '3' WHERE EDU_LEVEL LIKE '%9-13%'")
        cursor.execute("UPDATE demographics SET EDU_LEVEL = '5' WHERE EDU_LEVEL LIKE '%>=14%'")
        cursor.execute("UPDATE demographics SET EDU_LEVEL = '9' WHERE EDU_LEVEL IS NULL")
        cursor.execute("ALTER TABLE demographics ADD COLUMN EDU_LEVEL_NUM INTEGER")
        cursor.execute("UPDATE demographics SET EDU_LEVEL_NUM = CAST(EDU_LEVEL AS INTEGER)")
        cursor.execute("ALTER TABLE demographics DROP COLUMN EDU_LEVEL")
        cursor.execute("ALTER TABLE demographics RENAME COLUMN EDU_LEVEL_NUM TO EDU_LEVEL")
        db.commit()
        print(cursor.execute("SELECT EDU_LEVEL FROM demographics LIMIT 100").fetchall())
        db.close()
        exit()
    
    #
    quit()