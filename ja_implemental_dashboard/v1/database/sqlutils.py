import os, sys, time, datetime
import pandas
import sqlite3

def check_database_has_tables(connection: sqlite3.Connection, cohorts_required:bool=False) -> tuple[bool, list[str]]:
    """ Check if the database has the necessary tables.
    connection: sqlite3.Connection
        The connection to the database.
    cohorts_required: bool
        If True, the 'cohorts' table is required.

    Returns a tuple with two elements:
    - bool: True if the database has the necessary tables, False otherwise.
    - list[str]: the list of tables that are missing in the database (if True, empty list).
    """
    # required tables
    required_tables = ["demographics", "diagnoses", "interventions", "pharma", "physical_exams"]
    if cohorts_required:
        required_tables.append("cohorts")
    # logic
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [c[0] for c in cursor.fetchall()]
    missing_tables = [t for t in required_tables if t not in tables]
    del cursor
    return len(missing_tables) == 0, missing_tables

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

#### incomplete
def make_cohorts_table(connection: sqlite3.Connection):
    """ Create the cohorts table in the database.
    The table is created if it does not exist. If it does, it is replaced.
    connection: sqlite3.Connection
        The connection to the database.
        The database must have the following tables:
            demographics
            diagnoses
            interventions
            pharma
            physical_exams
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # logic
    cursor = connection.cursor()
    # drop cohorts table if it exists
    cursor.execute("DROP TABLE IF EXISTS cohorts;")
    connection.commit()
    # create the cohorts table
    # the table has the following columns:
    # - ID_SUBJECT: alphanumeric (could be non-unique in the table)
    # - YEAR_ENTRY: integer
    # - AGE_ENTRY: integer
    # - ID_COHORT: string
    # - ID_DISORDER: string
    query = """
        CREATE TABLE cohorts (
            ID_SUBJECT TEXT,
            YEAR_ENTRY INTEGER,
            AGE_ENTRY INTEGER,
            ID_COHORT TEXT,
            ID_DISORDER TEXT
        );
    """
    cursor.execute(query)
    connection.commit()
    # fill the table with the data
    ##################################################################################################################################

    
def stratify_demographics_sql(connection: sqlite3.Connection, **kwargs) -> pandas.Series:
    """ Given the demographics table, stratify the patients according to the kwargs parameters.
    This function outputs a pandas.Series of patient IDs that are compatible with the stratification parameters.
    kwargs:
    - year_of_inclusion: int
        The year of inclusion of the patients in the cohort.
    - age: tuple[int, int]
        (min_age, max_age), min_age included, max_age included
    - gender: str
        in ["A", "A-U", "M", "F", "U"]
    - civil status: str
        in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
    - job condition: str
        in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
    - educational level: str
        in ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]
    """
    # inputs
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    if year_of_inclusion is None:
        raise ValueError("year_of_inclusion must be provided")
    year_of_inclusion = int(year_of_inclusion)
    age = kwargs.get("age", None)
    if not isinstance(age, tuple):
        raise ValueError("age must be a tuple of two integers and must be provided")
    if len(age) != 2:
        raise ValueError("age must be a tuple of two integers and must be provided")
    _available_genders = ["A", "A-U", "M", "F", "U"]
    gender = kwargs.get("gender", None)
    if gender is None:
        raise ValueError("gender must be provided")
    if gender not in _available_genders:
        raise ValueError(f"gender must be in {_available_genders}")
    _available_civil_status = ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
    civil_status = kwargs.get("civil_status", None)
    if civil_status is None:
        raise ValueError("civil_status must be provided")
    if civil_status not in _available_civil_status:
        raise ValueError(f"civil_status must be in {_available_civil_status}")
    _available_job_conditions = ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
    job_condition = kwargs.get("job_condition", None)
    if job_condition is None:
        raise ValueError("job_condition must be provided")
    if job_condition not in _available_job_conditions:
        raise ValueError(f"job_condition must be in {_available_job_conditions}")
    _available_educational_levels = ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]
    educational_level = kwargs.get("educational_level", None)
    if educational_level is None:
        raise ValueError("educational_level must be provided")
    if educational_level not in _available_educational_levels:
        raise ValueError(f"educational_level must be in {_available_educational_levels}")
    # new logic with SQL - returns a list of PATIENT_ID s and the name of the created table that stores
    # the id of these patients
    cursor = connection.cursor()
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # create the table of stratified patients ids
    table_name = "stratified_patients"
    queries = []
    queries.append(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    age_selector_statement = f"(strftime('%Y', DT_BIRTH) <= {year_of_inclusion - age[0]} AND strftime('%Y', DT_BIRTH) >= {year_of_inclusion - age[1]})"
    # (20 <= 2015 - DT_BIRTH <= 80)
    age_selector_statement = f"({int(age[0])} <= {year_of_inclusion} - strftime('%Y', DT_BIRTH) <= {int(age[1])})"
    death_selector_statement = f"(strftime('%Y', DT_DEATH) > {year_of_inclusion} OR DT_DEATH IS NULL)"
    if gender == "A":
        gender_selector_statement = None
    elif gender == "A-U":
        gender_selector_statement = f"(GENDER IS NOT NULL)"
    elif gender == "U":
        gender_selector_statement = f"(GENDER IS NULL)"
    else:
        gender_selector_statement = f"(GENDER = '{gender}')"
    if civil_status == "All":
        civil_status_selector_statement = None
    elif civil_status == "All-Other":
        civil_status_selector_statement = f"(CIVIL_STATUS != 'Other')"
    else:
        civil_status_selector_statement = f"(CIVIL_STATUS = '{civil_status}')"
    if job_condition == "All":
        job_condition_selector_statement = None
    elif job_condition == "All-Unknown":
        job_condition_selector_statement = f"(JOB_COND IS NOT NULL)"
    elif job_condition == "Unknown":
        job_condition_selector_statement = f"(JOB_COND IS NULL)"
    else:
        job_condition_selector_statement = f"(JOB_COND = '{job_condition}')"
    if educational_level == "All":
        educational_level_selector_statement = None
    elif educational_level == "All-Unknown":
        educational_level_selector_statement = f"(EDU_LEVEL IS NOT NULL)"
    elif educational_level == "Unknown":
        educational_level_selector_statement = f"(EDU_LEVEL IS NULL)"
    else:
        educational_level_selector_statement = f"(EDU_LEVEL = '{educational_level}')"
    query = f"""
            CREATE TEMPORARY TABLE {table_name} AS
                SELECT DISTINCT ID_SUBJECT FROM demographics
    """
    where = False
    if age_selector_statement is not None:
        query += f" WHERE {age_selector_statement}"
        where = True
    if death_selector_statement is not None:
        connector = "AND" if where else "WHERE"
        query += f" {connector} {death_selector_statement}"
        where = True
    if gender_selector_statement is not None:
        connector = "AND" if where else "WHERE"
        query += f" {connector} {gender_selector_statement}"
        where = True
    if civil_status_selector_statement is not None:
        connector = "AND" if where else "WHERE"
        query += f" {connector} {civil_status_selector_statement}"
        where = True
    if job_condition_selector_statement is not None:
        connector = "AND" if where else "WHERE"
        query += f" {connector} {job_condition_selector_statement}"
        where = True
    if educational_level_selector_statement is not None:
        connector = "AND" if where else "WHERE"
        query += f" {connector} {educational_level_selector_statement}"
    queries.append(query)
    # execute the queries
    for q in queries:
        cursor.execute(q)
        connection.commit()
    # return the table name
    return table_name


# to finish


def make_age_startification_tables(connection: sqlite3.Connection, year_of_inclusions_list: list[int]|None=None, age_stratifications: list[tuple]|None=None, command: str="create"):
    """ Update the age stratification tables to speed up the process of stratifying by age, which is a current bottleneck.
    Age of patients is computed with respect to the year of inclusion.
    The created tables only contain the ID_SUBJECT of the patients that are in the age range.
    The tables are created if they do not exist, otherwise they are replaced.

    Inputs:
    - connection: sqlite3.Connection
        The connection to the database.
        The database must have the following tables:
            demographics
            diagnoses
            interventions
            pharma
            physical_exams
    - year_of_inclusions_list: list[int]
        The list of years of inclusion for the cohorts.
    - stratifications: list[tuple]
        The list of tuples with the stratification parameters.
        Each tuple has the following structure:
        (min_age_included, max_age_included)
    - command: str
        The command to execute. Can be "create" or "drop".
        If "create", the tables are created and overwritten if they exist.
        If "drop", the tables are dropped if they exist and are not created anew.
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # check input
    if age_stratifications is None:
        age_stratifications = [(0, 14), (15-18), (19-25), (26-40), (41-55), (56-65), (65, 150)]
    if year_of_inclusions_list is None:
        year_of_inclusions_list = [int(time.localtime().tm_year)]
    else:
        year_of_inclusions_list = [int(y) for y in year_of_inclusions_list]
    if command not in ["create", "drop"]:
        raise ValueError("command must be 'create' or 'drop'")
    # logic
    cursor = connection.cursor()
    # drop the tables if they exist
    all_tables = [a for a in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    for t in all_tables:
        if t[0].startswith("demographics_"):
            cursor.execute(f"DROP TABLE IF EXISTS {t[0]};")
            connection.commit()
    if command == "drop":
        cursor.close()
        return
    # create the tables:
    # for each patient in the demographics table, check if the patient is in the age range
    # for the different years of inclusion
    # naming convention example: demographics_2018_26_40
    for year_of_inclusion in year_of_inclusions_list:
        for age_stratification in age_stratifications:
            table_name = f"demographics_{int(year_of_inclusion)}_{int(age_stratification[0])}_{int(age_stratification[1])}"
            # create the table
            query = f"""
                CREATE TABLE {table_name} AS
                    SELECT DISTINCT ID_SUBJECT FROM demographics
                    WHERE (strftime('%Y', DT_BIRTH) <= {year_of_inclusion - age_stratification[0]} AND strftime('%Y', DT_BIRTH) >= {year_of_inclusion - age_stratification[1]})
                    AND (strftime('%Y', DT_DEATH) > {year_of_inclusion} OR DT_DEATH IS NULL);
            """
            cursor.execute(query)
            connection.commit()
    # close the connection
    cursor.close()

