import os
import numpy
import pandas

# INT_MH -> interventions
# INT_OTHER -> physical_exams

# File path
FILES_FOLDER = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia restricted\\"
cohorts_db = "cohorts.sas7bdat"
demographics_db = "demographics_restr.sas7bdat"
diagnoses_db = "diagnoses_restr.sas7bdat"
interventions_db = "interventions_restr.sas7bdat"
pharma_db = "pharma_restr.sas7bdat"
physical_exams_db = "physical_exams_restr.sas7bdat"

DB: dict[str: pandas.DataFrame] = {}

for f in [cohorts_db, demographics_db, diagnoses_db, interventions_db, pharma_db, physical_exams_db]:
    file_path = os.path.normpath(FILES_FOLDER + f)
    file_path = file_path.replace("\\", "/").replace("//", "/")
    file_path = os.path.normpath(file_path)
    # Read and parse file content
    df = pandas.read_sas(file_path)
    fn = os.path.splitext(f)[0].replace("_restr", "")
    DB[fn] = df

for k, v in DB.items():
    print(k)
    print(v.columns)
    print("\n")

class DropNa:
    def __init__(self):
        pass


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

DATETIME_NAN = pandas.to_datetime("1800-01-01")

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


# clean cohorts (the intermediate database)

DB["cohorts"] = preprocess_cohorts_database(DB["cohorts"])

# clean demographics

DB["demographics"] = preprocess_demographics_database(DB["demographics"])

# clean diagnoses

# to do

# clean pharma

# to do

# clean interventions (INTERVENTIONS / INT_MH)

DB["interventions"] = preprocess_interventions_database(DB["interventions"])

# clean physical exams (PHYSICAL_EXAMS / INT_OTHER)

# to do

print("Databases cleaned!")








########################
# REDUCE DATABASES SIZE
# - Since databases are quite huge, it would be stupid to compute the indicators on the whole database
# - We need to reduce the size of the databases by selecting only the rows that are compatible with the
# - problem at hand
########################

# to do








#######################################
# INDICATORS
#######################################

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
            raise ValueError("age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u']")
    elif isinstance(age, int):
        age = (age, age)
    elif isinstance(age, tuple):
        if len(age) != 2:
            raise ValueError("age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u']")
        age = (min(age), max(age))
    else:
        raise ValueError("age must be an integer, a tuple of two integers or a string in ['a', 'l', 'u']")
    gender = kwargs.get("gender", "A")
    if gender not in ["A", "A-U", "M", "F", "U"]:
        raise ValueError("gender must be in ['A', 'A-U', 'M', 'F', 'U']")
    civil_status = kwargs.get("civil_status", "All")
    if civil_status not in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]:
        raise ValueError("civil_status must be in ['All', 'All-Other', 'Unmarried', 'Married', 'Married_no_long', 'Other']")
    job_condition = kwargs.get("job_condition", "All")
    if job_condition not in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]:
        raise ValueError("job_condition must be in ['All', 'All-Unknown', 'Employed', 'Unemployed', 'Pension', 'Unknown']")
    educational_level = kwargs.get("educational_level", "All")
    if educational_level not in ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]:
        raise ValueError("educational_level must be in ['All', 'All-Unknown', '0-5', '6-8', '9-13', '>=14', 'Unknown']")
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

# MA1
if 0:
    disease_codes = ["SCHIZO", "DEPRE", "BIPOLAR"]
    available_years = list(set(DB["cohorts"]["YEAR_ENTRY"]))
    available_years.sort()
    ma1 = {}
    for d in disease_codes:
        ma1[d] = {}
        for y in available_years:
            row_idxs = (DB["cohorts"][d] == "Y") & (DB["cohorts"]["YEAR_ENTRY"] == y) & (DB["cohorts"]["PREVALENT"] == "Y")
            t_ = DB["cohorts"].loc[row_idxs, "ID_SUBJECT"]
            ma1[d][y] = t_.nunique()
    print("MA1", ma1)

# MA1 - full stratification (age is stratified later)
# this takes an awfully long time, but keep the logic for now
if 0:
    # disease, year, gender, civil status, job condition, educational level -> make dicts in this order
    DB["cohorts"]["YEAR_ENTRY"] = numpy.random.randint(2009, 2015, DB["cohorts"].shape[0]) #########################    just to check if plots work
    disease_codes = ["SCHIZO", "DEPRE", "BIPOLAR"]
    available_years = list(set(DB["cohorts"]["YEAR_ENTRY"]))
    available_years.sort()
    for d_ in disease_codes:
        ma1[d_] = {}
        for y_ in available_years:
            ma1[d_][y_] = {}
            for g_ in ["A", "M", "F", "U"]:
                ma1[d_][y_][g_] = {}
                for cs_ in ["All", "Unmarried", "Married", "Married_no_long", "Other"]:
                    ma1[d_][y_][g_][cs_] = {}
                    for jc_ in ["All", "Employed", "Unemployed", "Pension", "Unknown"]:
                        ma1[d_][y_][g_][cs_][jc_] = {}
                        for el_ in ["All", "0-5", "6-8", "9-13", ">=14", "Unknown"]:
                            ma1[d_][y_][g_][cs_][jc_][el_] = 0
                            # Find the subjects in the cohort
                            row_idxs = (DB["cohorts"][d_] == "Y") & (DB["cohorts"]["YEAR_ENTRY"] == y_) & (DB["cohorts"]["PREVALENT"] == "Y")
                            t_ = DB["cohorts"].loc[row_idxs, "ID_SUBJECT"]
                            t_ = t_.unique()
                            # select, from the demographics dataframe, all columns, but just the rows having ID_SUBJECT in t_
                            row_idxs = DB["demographics"]["ID_SUBJECT"].isin(t_)
                            t_ = DB["demographics"].loc[row_idxs, :]
                            # stratify from demographics
                            condition = pandas.DataFrame(True, index=t_.index, columns=["condition"])
                            # gender
                            if g_ == "A":
                                pass
                            else:
                                condition = condition & (t_["GENDER"] == g_)
                            # civil status
                            if cs_ == "All":
                                pass
                            else:
                                condition = condition & (t_["CIVIL_STATUS"] == cs_)
                            # job condition
                            if jc_ == "All":
                                pass
                            else:
                                condition = condition & (t_["JOB_COND"] == jc_)
                            # educational level
                            if el_ == "All":
                                pass
                            else:
                                condition = condition & (t_["EDU_LEVEL"] == el_)
                            # get number of survivors
                            ma1[d_][y_][g_][cs_][jc_][el_] = condition["condition"].sum()
                            


    # plot this bad boy with holoviwes
    import panel
    panel.extension("bokeh")
    import holoviews

    ma1_plots = {} # [disease][gender][civil status][job condition][educational level]
    for d_ in disease_codes:
        ma1_plots[d_] = {}
        for g_ in ["A", "M", "F", "U"]:
            ma1_plots[d_][g_] = {}
            for cs_ in ["All", "Unmarried", "Married", "Married_no_long", "Other"]:
                ma1_plots[d_][g_][cs_] = {}
                for jc_ in ["All", "Employed", "Unemployed", "Pension", "Unknown"]:
                    ma1_plots[d_][g_][cs_][jc_] = {}
                    for el_ in ["All", "0-5", "6-8", "9-13", ">=14", "Unknown"]:
                        ma1_plots[d_][g_][cs_][jc_][el_] =  holoviews.Curve(
                            (list(ma1[d_].keys()), [ma1[d_][y_][g_][cs_][jc_][el_] for y_ in ma1[d_].keys()]), label=f"{d_} {g_} {cs_} {jc_} {el_}"
                        ).opts(
                            line_width=10, line_color='indianred'
                        )
                        #
                        ma1_plots[d_][g_][cs_][jc_][el_].show()
                        quit()
                        





# MA2
if 0:
    disease_codes = ["SCHIZO", "DEPRE", "BIPOLAR"]
    available_years = list(set(DB["cohorts"]["YEAR_ENTRY"]))
    available_years.sort()
    ma2 = {}
    for d in disease_codes:
        ma2[d] = {}
        for y in available_years:
            row_idxs = (DB["cohorts"][d] == "Y") & (DB["cohorts"]["YEAR_ENTRY"] == y) & (DB["cohorts"]["INCIDENT"] == "Y")
            t_ = DB["cohorts"].loc[row_idxs, "ID_SUBJECT"]
            ma2[d][y] = t_.nunique()
    print("MA2", ma2)

    # MA3
    disease_codes = ["SCHIZO", "DEPRE", "BIPOLAR"]
    available_years = list(set(DB["cohorts"]["YEAR_ENTRY"]))
    available_years.sort()
    ma3 = {}
    for d in disease_codes:
        ma3[d] = {}
        for y in available_years:
            row_idxs = (DB["cohorts"][d] == "Y") & (DB["cohorts"]["YEAR_ENTRY"] == y) & (DB["cohorts"]["INCIDENT_1825"] == "Y")
            t_ = DB["cohorts"].loc[row_idxs, "ID_SUBJECT"]
            ma3[d][y] = t_.nunique()
    print("MA3", ma3)



# MA3


# MB2
if 0:

    available_diseases = ["SCHIZO", "DEPRE", "BIPOLAR"]
    # da guardare interventions (INT_MH)
    # per cross ref pazienti malattia guarda COHORTE per ora (pipeline completa sarebbe diagnoses)

    def mb2(**kwargs):
        # implementaz finale in monitoring.b2 diversa da questa
        """
        kwargs:
        passed from clean_indicator_getter_input
        output:
        dict[str: dict[str: int]]
        keys level 0: ["01", "02", "03", "04", "05", "06", "07", "Other"] # TYPE_INT levels
        keys level 1: ["total", "mean", "median", "std", "min", "max", "25%", "75%", "distribution"]
        """
        # inputs
        kwargs = clean_indicator_getter_input(**kwargs)
        tables = kwargs.get("dict_of_tables", None)
        disease_db_code = kwargs.get("disease_db_code", None)
        year_of_inclusion = kwargs.get("year_of_inclusion", None)
        age = kwargs.get("age", None)
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        type_int_list = ["01", "02", "03", "04", "05", "06", "07", "Other"]
        statistics_keys = ["total", "mean", "median", "std", "min", "max", "25%", "75%", "distribution"]
        output = {k0: {k1: 0 for k1 in statistics_keys} for k0 in type_int_list}
        # get a list of patient ids that are compatible with the stratificatio parameters
        valid_patient_ids = stratify_demographics(
            tables["demographics"],
            year_of_inclusion=year_of_inclusion,
            age=age,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        # stratify patients by disease: from valid_patient_ids, select only the ones that in the cohorts
        # table have at least one entry for the desired disease
        ids_with_disease: numpy.ndarray = tables["cohorts"].loc[
            (tables["cohorts"][disease_db_code] == "Y") & (tables["cohorts"]["YEAR_ENTRY"] <= year_of_inclusion),
            "ID_SUBJECT"
        ].unique()
        valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_with_disease)]
        # patients are stratified, now we have to check in the interventions table
        # for each row (representing a sanitary intervention) if the patient is in the list and how many times
        # the intervention is repeated
        for type_int in type_int_list:
            # get the rows of the interventions table that are compatible with the stratification parameters
            condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
            condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
            condition = condition & (tables["interventions"]["TYPE_INT"] == type_int)
            condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
            # get the number of interventions
            output[type_int]["total"] = condition.sum()
            if output[type_int]["total"] > 0:
                # get the distribution of the number of interventions
                val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
                output[type_int]["distribution"] = val_counts.to_list()
                # get the statistics
                output[type_int]["mean"] = val_counts.mean()
                output[type_int]["median"] = val_counts.median()
                
                output[type_int]["std"] = val_counts.std() if len(val_counts) > 1 else 0.0
                output[type_int]["min"] = val_counts.min()
                output[type_int]["max"] = val_counts.max()
                output[type_int]["25%"] = val_counts.quantile(0.25) if len(val_counts) > 1 else output[type_int]["median"]
                output[type_int]["75%"] = val_counts.quantile(0.75) if len(val_counts) > 1 else output[type_int]["median"]
            else:
                output[type_int]["distribution"] = [0, 0]
                output[type_int]["mean"] = 0
                output[type_int]["median"] = 0
                output[type_int]["std"] = 0
                output[type_int]["min"] = 0
                output[type_int]["max"] = 0
                output[type_int]["25%"] = 0
                output[type_int]["75%"] = 0
        # return
        return output

            
    # test this bad boy

    # make a holoviews plot
    import panel
    import holoviews
    holoviews.extension("bokeh")

    import warnings
    # Suppress FutureWarning messages
    warnings.simplefilter(action='ignore', category=FutureWarning)


    cohorts_rand = DB["cohorts"].copy(deep=True)
    cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
    database_dict = {
        "demographics": DB["demographics"],
        "diagnoses": DB["diagnoses"],
        "pharma": DB["pharma"],
        "interventions": DB["interventions"],
        "physical_exams": DB["physical_exams"],
        "cohorts": cohorts_rand
    }
    def build_plot(**kwargs):
        disease_dict = {
            "_schizophrenia_": "SCHIZO",
            "_depression_": "DEPRE",
            "_bipolar_disorder_": "BIPOLAR"
        }
        database_dict = kwargs.get("database_dict", None)
        disease_db_code = disease_dict[kwargs.get("disease_db_code", None)]
        # 
        py_data = []
        for y_ in range(2013, 2016):
            output = mb2(
                dict_of_tables=database_dict,
                disease_db_code=disease_db_code,
                year_of_inclusion=y_,
                age=kwargs.get("age_code", "a"),
                gender=kwargs.get("gender_code", "A"),
                civil_status=kwargs.get("civil_status", "All"),
                job_condition=kwargs.get("job_condition", "All"),
                educational_level=kwargs.get("educational_level", "All")
            )
            py_data.append(output)
        type_int_list = ["01", "02", "03", "04", "05", "06", "07", "Other"]
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'pink', 'gray']
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        c_ = []
        v_ = []
        for i, y_ in enumerate(range(2013, 2016)):
            for type_int in type_int_list:
                n = len(py_data[i][type_int]["distribution"])
                g_.extend([y_] * n)
                c_.extend([type_int] * n)
                v_.extend(py_data[i][type_int]["distribution"])

        plot = holoviews.BoxWhisker((g_, c_, v_), ["Year", "Type of Intervention"], "Distribution of the number of interventions").sort().opts(
            show_legend=False, width=600, box_fill_color=holoviews.dim("Type of Intervention"), cmap='Set1'
        ).opts(
            title="Median Interventions",
        )
        return panel.pane.HoloViews(plot)


    disease_widget = panel.widgets.Select(options=["_schizophrenia_", "_depression_", "_bipolar_disorder_"], name="Disease")
    age_widget = panel.widgets.Select(options=["a", "l", "u"], name="Age")
    gender_widget = panel.widgets.Select(options=["A", "A-U", "M", "F", "U"], name="Gender")
    civil_status_widget = panel.widgets.Select(options=["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"], name="Civil Status")
    job_condition_widget = panel.widgets.Select(options=["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"], name="Job Condition")
    educational_level_widget = panel.widgets.Select(options=["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"], name="Educational Level")

    widget_panel = panel.Column(
        disease_widget,
        age_widget,
        gender_widget,
        civil_status_widget,
        job_condition_widget,
        educational_level_widget,
        styles={
            "background-color": "#dadada",
            "padding": "10px",
            "border-radius": "10px",
            "border": "1px solid #a0a0a0",
            "max-width": "250px",
            "margin-right": "30px",
        }
    )

    app = panel.Row(
        panel.bind(
            build_plot,
            database_dict=database_dict,
            disease_db_code=disease_widget,
            age_code=age_widget,
            gender_code=gender_widget,
            civil_status=civil_status_widget,
            job_condition=job_condition_widget,
            educational_level=educational_level_widget
        ),
        widget_panel
    )

    app.show()
    quit()


    

# EA1

COHORT_CODE_TO_DB_COHORT_COLUMN = {
    "_a_": "PREVALENT",
    "_b_": "INCIDENT",
    "_c_": "INCIDENT_1825"
}

if 1:
    def ea1(**kwargs):
        """
        kwargs:
        passed from clean_indicator_getter_input
        output:
        dict[str: val]
        keys: ["percentage", "distribution"]
        """
        # inputs
        kwargs = clean_indicator_getter_input(**kwargs)
        tables = kwargs.get("dict_of_tables", None)
        disease_db_code = kwargs.get("disease_db_code", None)
        cohort_code = kwargs.get("cohort_code", None)
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
        ids_in_cohort: numpy.ndarray = tables["cohorts"].loc[tables["cohorts"][COHORT_CODE_TO_DB_COHORT_COLUMN[cohort_code]] == "Y", "ID_SUBJECT"].unique()
        valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_in_cohort)]
        # - percentage denominator: number of patients with valid patient ids
        denominator = valid_patient_ids.unique().shape[0]
        # - percentage numerator: number of patients with at least one intervention in the year of inclusion
        condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
        condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
        condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
        numerator = tables["interventions"].loc[condition, "ID_SUBJECT"].unique().shape[0]
        # - percentage
        output["percentage"] = numerator / denominator
        # - distribution: we use the same condition as before but we count the number of interventions per ID_SUBJECT
        val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
        if len(val_counts) > 0:
            output["distribution"] = val_counts.to_list()
        else:
            output["distribution"] = [0, 0]
        # return
        return output

    # test
    out = ea1(
        dict_of_tables=DB,
        disease_db_code="SCHIZO",
        cohort_code="_a_",
        year_of_inclusion=2015,
        age="a",
        gender="A",
        civil_status="All",
        job_condition="All",
        educational_level="All"
    )
    print(out)

    # test with holoviews for some years of inclusion
        # make a holoviews plot
    import panel
    import holoviews
    holoviews.extension("bokeh")
    import bokeh
    import warnings
    # Suppress FutureWarning messages
    warnings.simplefilter(action='ignore', category=FutureWarning)
    cohorts_rand = DB["cohorts"].copy(deep=True)
    cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
    database_dict = {
        "demographics": DB["demographics"],
        "diagnoses": DB["diagnoses"],
        "pharma": DB["pharma"],
        "interventions": DB["interventions"],
        "physical_exams": DB["physical_exams"],
        "cohorts": cohorts_rand
    }
    years = [int(y) for y in list(range(2013, 2016))]
    outs_per_year = []
    for y_ in years:
        out = ea1(
            dict_of_tables=database_dict,
            disease_db_code="SCHIZO",
            cohort_code="_a_",
            year_of_inclusion=y_,
            age="a",
            gender="A",
            civil_status="All",
            job_condition="All",
            educational_level="All"
        )
        outs_per_year.append(out)
    # make a line plot for percentage
    plot_line = (
        holoviews.Curve(
            (years, [100*o["percentage"] for o in outs_per_year]),
        ).opts(
            line_width=2, line_color='indianred',
        ) * holoviews.Scatter(
            (years, [100*o["percentage"] for o in outs_per_year]),
        ).opts(
            color='indianred', size=10,
            marker='o', line_width=2,
            tools=['hover']
        )
    ).opts(
        width=600,
        title="% of patients with at least one intervention",
        xlabel="Year of inclusion",
        ylabel="Percentage",
        show_legend=False,
        xlim=(years[0]-0.5, years[-1]+0.5),
        xticks=years,
        ylim=(0, 100),
        yformatter="%.0f%%"
    )
    # make a BoxWhisker plot for the distribution
    # above the boxwhisker plot there is a transparent scatterplot to show the tooltip info more easily
    mean_y = [numpy.mean(o["distribution"]) for o in outs_per_year]
    median_y = [numpy.median(o["distribution"]) for o in outs_per_year]
    std_y = [numpy.std(o["distribution"]) for o in outs_per_year]
    min_y = [numpy.min(o["distribution"]) for o in outs_per_year]
    max_y = [numpy.max(o["distribution"]) for o in outs_per_year]
    q25_y = []
    q75_y = []
    for o in outs_per_year:
        if len(o["distribution"]) > 1:
            q25_y.append(numpy.percentile(o["distribution"], 25))
            q75_y.append(numpy.percentile(o["distribution"], 75))
        else:
            q25_y.append(o["distribution"][0])
            q75_y.append(o["distribution"][0])
    scatter_for_tooltip = holoviews.Scatter(
        (years, mean_y, median_y, std_y, min_y, max_y, q25_y, q75_y),
        kdims=[("year", "Year"), ("mean", "Mean")], # x, y positions
        vdims=[
            ("mean", "Mean"), # (variable, name to display in the tooltip)
            ("median", "Median"), 
            ("std","Standard deviation"), 
            ("min", "Minimum"), 
            ("max", "Maximum"), 
            ("25%", "25th percentile"), 
            ("75%", "75th percentile")
        ]
        
    ).opts(
        color="#00000000", # transparent
        size=30, # quite big
        tools=['hover'],
        xlabel="",
        ylabel="",
    )
    # groups: the years
    # cathegory: none
    # value: the distribution of the number of interventions each year
    years_box = []
    distribution_box = []
    for i, y_ in enumerate(years):
        years_box.extend([int(y_)] * len(outs_per_year[i]["distribution"]))
        distribution_box.extend(outs_per_year[i]["distribution"])
    plot_box = (
        holoviews.BoxWhisker(
            (years_box, distribution_box), "year", "distribution"
        ).sort().opts(
            box_fill_color="#3b4cc0ff",
        ) * scatter_for_tooltip
    ).opts(
        title="Distribution of patient interventions per year",
        width=600,
        show_legend=False,
        xlim=(years[0]-0.5, years[-1]+0.5),
        xlabel="Year of inclusion",
        ylabel="",
        ylim=(0, max(distribution_box)+5),
    )
    # violin plot
    plot_violin = (
        holoviews.Violin(
            (years_box, distribution_box), "year", "distribution"
        ) * scatter_for_tooltip
    ).opts(
        title="Distribution of patient interventions per year",
        width=600,
        show_legend=False,
        xlim=(years[0]-0.5, years[-1]+0.5),
        xlabel="Year of inclusion",
        ylabel="",
        ylim=(-0.01, max(distribution_box)+5),
    )

    # show both
    app = panel.Tabs(
        ("EA1 Percentage", panel.pane.HoloViews(plot_line)),
        ("EA1 Distribution - Boxplot", panel.pane.HoloViews(plot_box)),
        ("EA1 Distribution - Violin", panel.pane.HoloViews(plot_violin)),
        styles={
            "margin-top": "40px",
            "margin-left": "20px",
            "width": "100%",
            "border": "1px solid #a0a0a0",
            "border-radius": "10px",
            "padding": "10px",
        }
    )
    app.show()
    quit()
        

