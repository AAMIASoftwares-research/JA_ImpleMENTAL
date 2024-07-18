# COMMON UTILITIES

from ..database.database import check_database_has_tables

### this function is a good idea but should be made much better,
### the allowed values should be parametrized somewhere 
### in the database package.
def clean_indicator_getter_input(**kwargs):
    """
    kwargs:
    - dict_of_tables: dict[str: pandas.DataFrame]
        keys: ["demographics", "diagnoses", "pharma", "interventions", "physical_exams", "cohorts"]
        required
    - disease_db_code: str
        in ["SCHIZO", "DEPRE", "BIPOLAR"]
        required
    - cohort_code: str
        in ["_a_", "_b_", "_c_"] corresponding to ["PREVALENT", "INCIDENT", "INCIDENT_1825"]
        default: "_a_"
    - year_of_inclusion: int
        required
    - age: int |tuple | str
        if int -> age
        if tuple -> (min_age, max_age), min_age included, max_age included
        if str -> in ["a", "l", "u"] -> all, less equal than 10 y.o., more equal than 90 y.o.
        default: "a"
    - gender: str
        in ["A", "A-U", "M", "F", "U"]
        default: "A"
    - civil status: str
        in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
        default: "All"
    - job condition: str
        in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
        default: "All"
    - educational level: str
        in ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]
        default: "All"
    """
    # inputs
    connection = kwargs.get("connection", None)
    if connection is None:
        raise ValueError("connection must be provided to get the indicator and it should be an sqlite3.Connection object.")
    cohorts_required = kwargs.get("cohorts_required", True)
    has_tables_, missing_tables_ = check_database_has_tables(connection, cohorts_required=cohorts_required)
    if not has_tables_:
        raise ValueError("The provided database does not have the required tables to get the indicator. Missing tables: " + ", ".join(missing_tables_))
    disease_db_code = kwargs.get("disease_db_code", None)
    if disease_db_code is None:
        raise ValueError("disease_db_code must be provided")
    if disease_db_code not in ["SCHIZO", "DEPRE", "BIPOLAR"]:
        raise ValueError("disease_db_code must be in ['SCHIZO', 'DEPRE', 'BIPOLAR']")
    cohort_code = kwargs.get("cohort_code", "_a_")
    if cohort_code not in ["_a_", "_b_", "_c_"]:
        raise ValueError("cohort_code must be in ['_a_', '_b_', '_c_'] corresponding to ['PREVALENT', 'INCIDENT', 'INCIDENT_1825']")
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    if year_of_inclusion is None:
        raise ValueError("year_of_inclusion must be provided")
    year_of_inclusion = int(year_of_inclusion)
    age = kwargs.get("age", "All")
    gender = kwargs.get("gender", "A")
    if gender not in ["A", "A-U", "M", "F", "U"]:
        raise ValueError(f"gender must be in ['A', 'A-U', 'M', 'F', 'U'], got {gender} instead")
    civil_status = kwargs.get("civil_status", "All")
    if civil_status not in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]:
        raise ValueError(f"civil_status must be in ['All', 'All-Other', 'Unmarried', 'Married', 'Married_no_long', 'Other'], got {civil_status} instead")
    job_condition = kwargs.get("job_condition", "All")
    if job_condition not in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]:
        raise ValueError(f"job_condition must be in ['All', 'All-Unknown', 'Employed', 'Unemployed', 'Pension', 'Unknown'], got {job_condition} instead")
    educational_level = kwargs.get("educational_level", "All")
    if educational_level not in ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]:
        raise ValueError(f"educational_level must be in ['All', 'All-Unknown', '0-5', '6-8', '9-13', '>=14', 'Unknown'], got {educational_level} instead")
    # output
    return {
        "connection": connection,
        "disease_db_code": disease_db_code,
        "cohort_code": cohort_code,
        "year_of_inclusion": year_of_inclusion,
        "age": age,
        "gender": gender,
        "civil_status": civil_status,
        "job_condition": job_condition,
        "educational_level": educational_level
    }



def get_years_of_inclusion(connection):
    """
    connection: sqlite3.Connection
    """
    # todo: implement this function
    pass