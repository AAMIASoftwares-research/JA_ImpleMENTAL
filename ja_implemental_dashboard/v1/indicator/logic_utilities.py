import pandas

from ..database.database import DATETIME_NAN


# COMMON UTILITIES

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
    tables = kwargs.get("dict_of_tables", None)
    if tables is None:
        raise ValueError("dict_of_tables must be provided")
    if not isinstance(tables, dict):
        raise ValueError("dict_of_tables must be a dictionary")
    if not all([k in tables.keys() for k in ["demographics", "diagnoses", "pharma", "interventions", "physical_exams", "cohorts"]]):
        raise ValueError("dict_of_tables must contain all the keys: ['demographics', 'diagnoses', 'pharma', 'interventions', 'physical_exams', 'cohorts']")
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
    age = kwargs.get("age", "a")
    if age == "a":
        age = (0, 150)
    elif age == "l":
        age = (0, 10)
    elif age == "u":
        age = (90, 150)
    elif isinstance(age, str):
        if age not in ["a", "l", "u"]:
            raise ValueError(f"age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u'], got {age} instead")
    elif isinstance(age, int):
        age = (age, age)
    elif isinstance(age, tuple):
        if len(age) != 2:
            raise ValueError(f"age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u'], got {age} instead")
        age = (min(age), max(age))
    else:
        raise ValueError(f"age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u'], got {age} instead")
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
        "dict_of_tables": tables,
        "disease_db_code": disease_db_code,
        "cohort_code": cohort_code,
        "year_of_inclusion": year_of_inclusion,
        "age": age,
        "gender": gender,
        "civil_status": civil_status,
        "job_condition": job_condition,
        "educational_level": educational_level
    }

def stratify_demographics(demographics: pandas.DataFrame, **kwargs) -> pandas.Series:
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
