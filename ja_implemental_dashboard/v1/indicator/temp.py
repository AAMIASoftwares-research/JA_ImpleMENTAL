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

available_diseases = ["SCHIZO", "DEPRE", "BIPOLAR"]
# da guardare interventions (INT_MH)
# per cross ref pazienti malattia guarda COHORTE per ora (pipeline completa sarebbe diagnoses)

def clean_indicator_getter_input(**kwargs):
    """
    kwargs:
    - dict_of_tables: dict[str: pandas.DataFrame]
        keys: ["demographics", "diagnoses", "pharma", "interventions", "physical_exams", "cohorts"]
        required
    - disease_db_code: str
        in ["SCHIZO", "DEPRE", "BIPOLAR"]
        required
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
        "year_of_inclusion": year_of_inclusion,
        "age": age,
        "gender": gender,
        "civil_status": civil_status,
        "job_condition": job_condition,
        "educational_level": educational_level
    }

def mb2(**kwargs):
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
    # to do so we use the demographics database
    condition = pandas.Series(True, index=tables["demographics"].index, name="condition")
    # - age at the year of inclusion
    condition = condition & (tables["demographics"]["DT_BIRTH"].dt.year <= year_of_inclusion - age[0])
    condition = condition & (tables["demographics"]["DT_BIRTH"].dt.year >= year_of_inclusion - age[1])
    # - death at the year of inclusion
    condition = condition & ((tables["demographics"]["DT_DEATH"].dt.year >= year_of_inclusion) | (tables["demographics"]["DT_DEATH"].dt.year != DATETIME_NAN.year))
    # - gender
    if gender == "A":
        pass
    elif gender == "A-U":
        condition = condition & (tables["demographics"]["GENDER"] != "U")
    elif gender in ["M", "F", "U"]:
        condition = condition & (tables["demographics"]["GENDER"] == gender)
    # - civil status
    if civil_status == "All":
        pass
    elif civil_status == "All-Other":
        condition = condition & (tables["demographics"]["CIVIL_STATUS"] != "Other")
    else:
        condition = condition & (tables["demographics"]["CIVIL_STATUS"] == civil_status)
    # - job condition
    if job_condition == "All":
        pass
    elif job_condition == "All-Unknown":
        condition = condition & (tables["demographics"]["JOB_COND"] != "Unknown")
    else:
        condition = condition & (tables["demographics"]["JOB_COND"] == job_condition)
    # - educational level
    if educational_level == "All":
        pass
    elif educational_level == "All-Unknown":
        condition = condition & (tables["demographics"]["EDU_LEVEL"] != "Unknown")
    else:
        condition = condition & (tables["demographics"]["EDU_LEVEL"] == educational_level)
    # - get the list of IDs
    valid_patient_ids = pandas.Series(tables["demographics"].loc[condition, "ID_SUBJECT"].unique())
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
            output[type_int]["distribution"] = [0]
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


    

