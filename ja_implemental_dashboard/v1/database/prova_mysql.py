import os, sys, time
import numpy
import pandas
import panel

from .database import DISEASE_CODE_TO_DB_CODE, COHORT_CODE_TO_DB_CODE, DATETIME_NAN
from ..indicator.logic_utilities import clean_indicator_getter_input, stratify_demographics



# indicator logic
def ea1(**kwargs):
    """
    output dict:
    - percentage (float): the indicator, ranage [0; 1]; 
    - distribution (list): the distribution of number of intervention per patient
    if the patient has at least one intervention
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    tables = kwargs.get("dict_of_tables", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    cohort_db_code = COHORT_CODE_TO_DB_CODE[kwargs.get("cohort_code", None)]
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    # type_int: any intervention
    # percentage (float): the indicator, ranage [0; 1]; 
    # distribution (list): the distribution of number of intervention per patient
    #  if the patient has at least one intervention
    statistics_keys = ["percentage", "distribution"]
    output = {k0: None for k0 in statistics_keys}
    # logic
    # - get a list of patient ids that are compatible with the stratification parameters
    valid_patient_ids = stratify_demographics(
        tables["demographics"],
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    # - stratify patients by disease: from valid_patient_ids, select only the ones that in the cohorts
    # table have at least one entry for the desired disease
    ids_with_disease: numpy.ndarray = tables["cohorts"].loc[
        (tables["cohorts"][disease_db_code] == "Y") & (tables["cohorts"]["YEAR_ENTRY"] <= year_of_inclusion),
        "ID_SUBJECT"
    ].unique()
    valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_with_disease)]
    # - stratify by patient cohort (_a_, _b_, _c_)
    ids_in_cohort: numpy.ndarray = tables["cohorts"].loc[tables["cohorts"][cohort_db_code] == "Y", "ID_SUBJECT"].unique()
    valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_in_cohort)]
    # - percentage denominator: number of patients with valid patient ids
    denominator = valid_patient_ids.unique().shape[0]
    # - percentage numerator: number of patients with at least one intervention in the year of inclusion
    condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
    condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
    condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
    numerator = tables["interventions"].loc[condition, "ID_SUBJECT"].unique().shape[0]
    # - percentage
    output["percentage"] = numerator / denominator if denominator > 0 else 0.0
    # - distribution: we use the same condition as before but we count the number of interventions per ID_SUBJECT
    val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
    if len(val_counts) > 0:
        output["distribution"] = val_counts.to_list()
    else:
        output["distribution"] = [0, 0]
    # return
    return output




import sqlite3



def stratify_demographics_mysql(demographics: pandas.DataFrame, **kwargs) -> pandas.Series:
    """ Given the demographics table, stratify the patients according to the kwargs parameyers.
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
        raise ValueError("year_of_inclusion must be a tuple of two integers and must be provided")
    if len(age) != 2:
        raise ValueError("year_of_inclusion must be a tuple of two integers and must be provided")
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
    # logic
    #################################
    ##################################
    #################################
    # get a list of patient ids that are compatible with the stratification parameters
    condition = pandas.Series(True, index=demographics.index, name="condition")
    # - age at the year of inclusion
    condition = condition & (demographics["DT_BIRTH"].dt.year <= year_of_inclusion - age[0])
    condition = condition & (demographics["DT_BIRTH"].dt.year >= year_of_inclusion - age[1])
    # - death after the year of inclusion or not deadm (DATETIME_NAN means not dead)
    condition = condition & ((demographics["DT_DEATH"].dt.year >= year_of_inclusion) | (demographics["DT_DEATH"].dt.year != DATETIME_NAN.year))
    # - gender
    if gender == "A":
        pass
    elif gender == "A-U":
        condition = condition & (demographics["GENDER"] != "U")
    elif gender in ["M", "F", "U"]:
        condition = condition & (demographics["GENDER"] == gender)
    # - civil status
    if civil_status == "All":
        pass
    elif civil_status == "All-Other":
        condition = condition & (demographics["CIVIL_STATUS"] != "Other")
    else:
        condition = condition & (demographics["CIVIL_STATUS"] == civil_status)
    # - job condition
    if job_condition == "All":
        pass
    elif job_condition == "All-Unknown":
        condition = condition & (demographics["JOB_COND"] != "Unknown")
    else:
        condition = condition & (demographics["JOB_COND"] == job_condition)
    # - educational level
    if educational_level == "All":
        pass
    elif educational_level == "All-Unknown":
        condition = condition & (demographics["EDU_LEVEL"] != "Unknown")
    else:
        condition = condition & (demographics["EDU_LEVEL"] == educational_level)
    # get the list of IDs
    valid_patient_ids = pandas.Series(demographics.loc[condition, "ID_SUBJECT"].unique())
    return valid_patient_ids

def ea1_mysql(**kwargs):
    """
    output dict:
    - percentage (float): the indicator, ranage [0; 1]; 
    - distribution (list): the distribution of number of intervention per patient
    if the patient has at least one intervention
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    tables = kwargs.get("dict_of_tables", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    cohort_db_code = COHORT_CODE_TO_DB_CODE[kwargs.get("cohort_code", None)]
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    # type_int: any intervention
    # percentage (float): the indicator, ranage [0; 1]; 
    # distribution (list): the distribution of number of intervention per patient
    #  if the patient has at least one intervention
    statistics_keys = ["percentage", "distribution"]
    output = {k0: None for k0 in statistics_keys}
    # logic
    # - get a list of patient ids that are compatible with the stratification parameters
    valid_patient_ids = stratify_demographics_mysql(
        tables["demographics"],
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    return valid_patient_ids #############################################à
    if 0:
        # - stratify patients by disease: from valid_patient_ids, select only the ones that in the cohorts
        # table have at least one entry for the desired disease
        ids_with_disease: numpy.ndarray = tables["cohorts"].loc[
            (tables["cohorts"][disease_db_code] == "Y") & (tables["cohorts"]["YEAR_ENTRY"] <= year_of_inclusion),
            "ID_SUBJECT"
        ].unique()
        valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_with_disease)]
        # - stratify by patient cohort (_a_, _b_, _c_)
        ids_in_cohort: numpy.ndarray = tables["cohorts"].loc[tables["cohorts"][cohort_db_code] == "Y", "ID_SUBJECT"].unique()
        valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_in_cohort)]
        # - percentage denominator: number of patients with valid patient ids
        denominator = valid_patient_ids.unique().shape[0]
        # - percentage numerator: number of patients with at least one intervention in the year of inclusion
        condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
        condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
        condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
        numerator = tables["interventions"].loc[condition, "ID_SUBJECT"].unique().shape[0]
        # - percentage
        output["percentage"] = numerator / denominator if denominator > 0 else 0.0
        # - distribution: we use the same condition as before but we count the number of interventions per ID_SUBJECT
        val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
        if len(val_counts) > 0:
            output["distribution"] = val_counts.to_list()
        else:
            output["distribution"] = [0, 0]
        # return
        return output






if __name__ == "__main__" and 0:
    # load the tables in the mysql database (create the tables if they do not exist)
    # - connect to the database to load all example tables in it
    from .database import FILES_FOLDER
    conn = sqlite3.connect('EXAMPLE.db')
    cursor = conn.cursor()
    # import file names with .csv extension
    files = os.listdir(FILES_FOLDER)
    files = [f0 for f0 in files if f0.endswith(".csv")]
    # load csv data in the database in a tables with the same name as the file
    for f0 in files:
        table_name = f0.replace(".csv", "")
        df = pandas.read_csv(os.path.join(FILES_FOLDER, f0))
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    # - close the connection
    conn.commit()
    conn.close()
    #
    quit()






# test ea1 function - old
if __name__ == "__main__" and 0:
    from .database import FILES_FOLDER, DATABASE_FILENAMES_DICT, read_databases, preprocess_demographics_database, preprocess_interventions_database, preprocess_cohorts_database

    t0 = time.time()
    db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
    db["demographics"] = preprocess_demographics_database(db["demographics"])
    db["interventions"] = preprocess_interventions_database(db["interventions"])
    db["cohorts"] = preprocess_cohorts_database(db["cohorts"])
    # - a little data augmentation to better display the dashboard
    cohorts_rand = db["cohorts"].copy(deep=True)
    cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
    __DB__ = {
        "demographics": db["demographics"],
        "diagnoses": db["diagnoses"],
        "pharma": db["pharma"],
        "interventions": db["interventions"],
        "physical_exams": db["physical_exams"],
        "cohorts": cohorts_rand
    }
    print("data loading time:", time.time() - t0)
    # save to csv (just once)
    if 0:
        for k0, v0 in __DB__.items():
            v0.to_csv(f"{k0}.csv")

    # test old function
    t0 = time.time()
    res = ea1(
        dict_of_tables=__DB__,
        language_code="en",
        disease_db_code="DEPRE",
        cohort_code="_a_",
        year_of_inclusion=2015,
        age=(50, 80),
        gender="A",
        civil_status="All",
        job_condition="All",
        educational_level="All"
    )
    print("old function time:", time.time() - t0)

    # make data for new function
    conn = sqlite3.connect('EXAMPLE.db')
    cursor = conn.cursor()
    if 0:
        # save _DB_ to the database
        for k0, v0 in __DB__.items():
            v0.to_sql(k0, conn, if_exists='replace', index=False)
        # - close the connection
        conn.commit()
    conn.close()





# test ea1 function - new with sqlite3
if __name__ == "__main__":
    t0 = time.time()
    conn = sqlite3.connect('EXAMPLE.db')
    cursor = conn.cursor()
    print("connection time:", time.time() - t0)
    # check names of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    t0 = time.time()
    cursor.execute("SELECT gender FROM demographics;")
    result_list = [a[0] for a in cursor.fetchall()]
    print("new function time for gender selection:", time.time() - t0)
    print(result_list[:20])

    # example: select all patients (stratify) that have certain properties
    t0 = time.time()
    query_list = [
        "DROP TABLE IF EXISTS temp;",
        "DROP TABLE IF EXISTS temp2;",
        """
        CREATE TABLE temp AS
            SELECT ID_SUBJECT
            FROM demographics
            WHERE
                (20 <= 2015 - DT_BIRTH <= 80)
                AND
                (DT_DEATH >= 2015 OR DT_DEATH IS NULL)
                AND
                (GENDER = 'M' OR GENDER = 'F')
                AND
                (CIVIL_STATUS = 'Married')
                AND
                (JOB_COND = 'Employed')
                AND
                (EDU_LEVEL = '9-13')
        """,
        """
        CREATE TABLE temp2 AS
            SELECT ID_SUBJECT
            FROM cohorts
            WHERE
                DEPRE = 'Y'
                AND
                ID_SUBJECT IN (SELECT ID_SUBJECT FROM temp)
        """,
        """
        DROP TABLE temp
        """,
        """
        SELECT COUNT(DISTINCT ID_SUBJECT) FROM temp2
        """,
        """
        DROP TABLE temp2
        """
    ]
    r_list = [cursor.execute(q).fetchall() for q in query_list]
    result_list = r_list[-2]
    print("new function time for patient stratification:", time.time() - t0)
    print(result_list[:20])
    print("length of result_list:", len(result_list))




    
    """
    from .database import FILES_FOLDER, DATABASE_FILENAMES_DICT, read_databases, preprocess_demographics_database, preprocess_interventions_database, preprocess_cohorts_database
    db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
    db["demographics"] = preprocess_demographics_database(db["demographics"])
    db["interventions"] = preprocess_interventions_database(db["interventions"])
    db["cohorts"] = preprocess_cohorts_database(db["cohorts"])
    # - a little data augmentation to better display the dashboard
    cohorts_rand = db["cohorts"].copy(deep=True)
    cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
    __DB__ = {
        "demographics": db["demographics"],
        "diagnoses": db["diagnoses"],
        "pharma": db["pharma"],
        "interventions": db["interventions"],
        "physical_exams": db["physical_exams"],
        "cohorts": cohorts_rand
    }
    t0 = time.time()
    res = ea1_mysql(
        dict_of_tables=__DB__,
        language_code="en",
        disease_db_code="DEPRE",
        cohort_code="_a_",
        year_of_inclusion=2015,
        age=(20, 80),
        gender="A",
        civil_status="Married",
        job_condition="Employed",
        educational_level="9-13"
    )
    print("time to fect stratifiction with pandas:", time.time() - t0)
    print(res[:20])
    print("length of result_list:", len(res))
    """


    conn.close()
    quit()

