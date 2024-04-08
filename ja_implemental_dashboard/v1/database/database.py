import os
import pandas

FILES_FOLDER = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia restricted\\"

DEMOGRAPHICS_DB_FILENAME = "demographics_restr.sas7bdat"
DIAGNOSES_DB_FILENAME = "diagnoses_restr.sas7bdat"
INTERVENTIONS_DB_FILENAME = "interventions_restr.sas7bdat"
PHARMA_DB_FILENAME = "pharma_restr.sas7bdat"
PHYSICAL_EXAMS_DB_FILENAME = "physical_exams_restr.sas7bdat"

COHORST_DB_FILENAME = "cohorts.sas7bdat"


############
# CONSTANTS
############

DISEASE_CODE_TO_DB_CODE = {
    "_schizophrenia_": "SCHIZO",
    "_depression_": "DEPRE",
    "_bipolar_disorder_": "BIPOLAR"
}

COHORT_CODE_TO_DB_CODE = {
    "_a_": "INCIDENT",
    "_b_": "PREVALENT",
    "_c_": "INCIDENT_1825"
}


#################################
# READ SAS DATABASES WITH PANDAS
#################################

DATABASE_FILENAMES_DICT = {
    "demographics": DEMOGRAPHICS_DB_FILENAME,
    "diagnoses": DIAGNOSES_DB_FILENAME,
    "interventions": INTERVENTIONS_DB_FILENAME,
    "pharma": PHARMA_DB_FILENAME,
    "physical_exams": PHYSICAL_EXAMS_DB_FILENAME,
    "cohorts": COHORST_DB_FILENAME,
}


def read_databases(databases_dict: dict[str: str], files_folder):
    """ Read databases from files and return a dictionary with the dataframes in this format:
    {
        "demographics": dataframe,
        "diagnoses": dataframe,
        "interventions": dataframe,
        "pharma": dataframe,
        "physical_exams": dataframe,
        "cohorts": dataframe,
    }

    Args:
        databases_dict (dict[str: str]): A dictionary with the database names as keys and the filenames as values
        files_folder (str): The folder where the files are stored
    """
    allowed_keys = ["demographics", "diagnoses", "interventions", "pharma", "physical_exams", "cohorts"]
    for k in databases_dict.keys():
        if k not in allowed_keys:
            raise ValueError(f"Key {k} of input dict is not allowed. Allowed keys are {allowed_keys}")
    input_keys_list = list(databases_dict.keys())
    for k in allowed_keys[:-1]:
        # cohorts is not strictly required
        if k not in input_keys_list:
            raise ValueError(f"Key {k} of input dict is missing. Required keys are {allowed_keys[:-1]}")
    db = {}
    for dbkey, f in databases_dict.items():
        file_path = os.path.normpath(FILES_FOLDER + f)
        file_path = file_path.replace("\\", "/").replace("//", "/")
        file_path = os.path.normpath(file_path)
        # Read and parse file content
        df = pandas.read_sas(file_path)
        db[dbkey] = df
    return db


########################
# REDUCE DATABASES SIZE
# - Since databases are quite huge, it would be stupid to compute the indicators on the whole database
# - We need to reduce the size of the databases by selecting only the rows that are compatible with the
# - problem at hand
########################

# to do


##################
# CLEAN DATABASES
##################

class DropNa:
    """Class that is just used as a flag to drop NA values from the dataframes"""
    def __init__(self):
        pass

DATETIME_NAN = pandas.to_datetime("1800-01-01")

def clean_alphanumeric(x: pandas.DataFrame | pandas.Series, fillnan=None) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series
    Alphanumeric
    if fillnan == DropNa class then drop the rows with NaN values
    """
    x_new = pandas.DataFrame(x)
    if fillnan is not None:
        if fillnan == DropNa:
            x_new.dropna(inplace=True)
        else:
            x_new.fillna(fillnan, inplace=True)
    x_new = (
        x_new
        .astype(str)                # from bytes to python strings
        .map(lambda x: x.strip())   # remove leading and trailing empty spaces
    )
    return x_new

def clean_numeric(x: pandas.DataFrame | pandas.Series, dtype: type|None = None, fillnan=None) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series
    Numeric
    if fillnan == DropNa class then drop the rows with NaN values
    """
    x_new = pandas.DataFrame(x)
    if fillnan is not None:
        if fillnan == DropNa:
            x_new.dropna(inplace=True)
        else:
            x_new.fillna(fillnan, inplace=True)
    if dtype is not None:
        x_new = x_new.astype(dtype)
    return x_new

def clean_datetime(x: pandas.DataFrame | pandas.Series) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series containing datetime information
    """
    x_new = pandas.DataFrame(x).fillna(DATETIME_NAN)
    for cols in x_new.columns:
        x_new[cols] = pandas.to_datetime(x_new[cols]).astype('datetime64[s]')
    return x_new

def preprocess_cohorts_database(cohort: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Merges and preprocesses the cohorts databases.
    """
    # Merge all the cohorts databases
    if isinstance(cohort, list):
        new = pandas.concat(cohort, axis=0)
    elif isinstance(cohort, pandas.DataFrame):
        new = cohort.copy(deep=True)
    else:
        raise ValueError("cohorts_list must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["YEAR_ENTRY"] = clean_numeric(new["YEAR_ENTRY"], dtype=int, fillnan=DropNa)
    new["PREVALENT"] = clean_alphanumeric(new["PREVALENT"], fillnan=DropNa)
    new["INCIDENT"] = clean_alphanumeric(new["INCIDENT"], fillnan=DropNa)
    new["INCIDENT_1825"] = clean_alphanumeric(new["INCIDENT_1825"], fillnan=DropNa)
    new["SCHIZO"] = clean_alphanumeric(new["SCHIZO"], fillnan="N")
    new["DEPRE"] = clean_alphanumeric(new["DEPRE"], fillnan="N")
    new["BIPOLAR"] = clean_alphanumeric(new["BIPOLAR"], fillnan="N")
    return new

def preprocess_demographics_database(demographics: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Preprocesses the demographics database.
    """
    # Merge all the demographics databases
    if isinstance(demographics, list):
        new = pandas.concat(demographics, axis=0)
    elif isinstance(demographics, pandas.DataFrame):
        new = demographics.copy(deep=True)
    else:
        raise ValueError("demographics must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["DT_BIRTH"] = clean_datetime(new["DT_BIRTH"])
    new["DT_DEATH"] = clean_datetime(new["DT_DEATH"])
    new["CAUSE_DEATH_1"] = clean_alphanumeric(new["CAUSE_DEATH_1"], fillnan="Unknown")
    new["CAUSE_DEATH_2"] = clean_alphanumeric(new["CAUSE_DEATH_2"], fillnan="Unknown")
    new["DT_START_ASSIST"] = clean_datetime(new["DT_START_ASSIST"])
    new["DT_END_ASSIST"] = clean_datetime(new["DT_END_ASSIST"])
    new["GENDER"] = clean_alphanumeric(new["GENDER"], fillnan="U")
    new["CIVIL_STATUS"] = clean_alphanumeric(new["CIVIL_STATUS"], fillnan="Other")
    new["JOB_COND"] = clean_alphanumeric(new["JOB_COND"], fillnan="Unknown")
    new["EDU_LEVEL"] = clean_alphanumeric(new["EDU_LEVEL"], fillnan="Unknown")
    return new

def preprocess_interventions_database(interventions: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Preprocesses the interventions database.
    """
    # Merge all the interventions databases
    if isinstance(interventions, list):
        new = pandas.concat(interventions, axis=0)
    elif isinstance(interventions, pandas.DataFrame):
        new = interventions.copy(deep=True)
    else:
        raise ValueError("interventions must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["DT_INT"] = clean_datetime(new["DT_INT"])
    new["TYPE_INT"] = clean_alphanumeric(new["TYPE_INT"], fillnan="Unknown")
    new["STRUCTURE"] = clean_alphanumeric(new["STRUCTURE"], fillnan="Unknown")
    new["OPERATOR_1"] = clean_alphanumeric(new["OPERATOR_1"], fillnan="Unknown")
    new["OPERATOR_2"] = clean_alphanumeric(new["OPERATOR_2"], fillnan="Unknown")
    new["OPERATOR_3"] = clean_alphanumeric(new["OPERATOR_3"], fillnan="Unknown")
    return new






if __name__ == "__main__":
    db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
    db["demographics"] = preprocess_demographics_database(db["demographics"])
    db["interventions"] = preprocess_interventions_database(db["interventions"])
    db["cohorts"] = preprocess_cohorts_database(db["cohorts"])
    print("demographics:\n", db["demographics"].head())
    print("interventions:\n", db["interventions"].head())
    print("cohorts:\n", db["cohorts"].head())