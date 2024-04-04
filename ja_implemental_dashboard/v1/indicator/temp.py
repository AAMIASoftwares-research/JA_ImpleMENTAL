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

DB = {}

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

# clean cohorts
DB["cohorts"]["ID_SUBJECT"] = DB["cohorts"]["ID_SUBJECT"].astype(int).astype(str)
DB["cohorts"]["YEAR_ENTRY"] = DB["cohorts"]["YEAR_ENTRY"].astype(int)
DB["cohorts"]["PREVALENT"] = DB["cohorts"]["PREVALENT"].astype(str)
DB["cohorts"]["INCIDENT"] = DB["cohorts"]["INCIDENT"].astype(str)
DB["cohorts"]["INCIDENT_1825"] = DB["cohorts"]["INCIDENT_1825"].astype(str)
DB["cohorts"]["SCHIZO"].fillna("N", inplace=True)
DB["cohorts"]["SCHIZO"] = DB["cohorts"]["SCHIZO"].astype(str)
DB["cohorts"]["DEPRE"].fillna("N", inplace=True)
DB["cohorts"]["DEPRE"] = DB["cohorts"]["DEPRE"].astype(str)
DB["cohorts"]["BIPOLAR"].fillna("N", inplace=True)
DB["cohorts"]["BIPOLAR"] = DB["cohorts"]["BIPOLAR"].astype(str)

# clean demographics
print(DB["demographics"].columns)

DB["demographics"]["ID_SUBJECT"] = DB["demographics"]["ID_SUBJECT"].astype(int).astype(str)
DB["demographics"]["DT_BIRTH"].fillna(pandas.to_datetime("1800-01-01"), inplace=True)
DB["demographics"]["DT_BIRTH"] = pandas.to_datetime(DB["demographics"]["DT_BIRTH"]).astype('datetime64[s]')
DB["demographics"]["GENDER"].fillna("U", inplace=True)
DB["demographics"]["GENDER"] = DB["demographics"]["GENDER"].astype(str)
DB["demographics"]["CIVIL_STATUS"].fillna("Other", inplace=True)
DB["demographics"]["CIVIL_STATUS"] = DB["demographics"]["CIVIL_STATUS"].astype(str)
DB["demographics"]["JOB_COND"].fillna("Unknown", inplace=True)
DB["demographics"]["JOB_COND"] = DB["demographics"]["JOB_COND"].astype(str)
DB["demographics"]["EDU_LEVEL"].fillna("Unknown", inplace=True)
DB["demographics"]["EDU_LEVEL"] = DB["demographics"]["EDU_LEVEL"].astype(str)



# MA1
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


