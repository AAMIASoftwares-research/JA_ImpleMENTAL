import os, sys
import pandas

DATA_FOLDER = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/"
)
FILE_NAME = "Indicatore 1_BIPO_coorteA.sas7bdat"

FILE = os.path.join(DATA_FOLDER, FILE_NAME)

# Open the dataset
df = pandas.read_sas(FILE)

# Data type cleaning
df["ID_ASSISTITO"] = df["ID_ASSISTITO"].astype(int) # Convert to int type
df["SESSO"] = df["SESSO"].astype(str) # Convert to string type (a character variable)
idx_DT_NASCITA_is_NaT = df["DT_NASCITA"].isna() # Find the index of NaT values
idx_DT_INIZIO_ASSISTENZA_is_NaT = df["DT_INIZIO_ASSISTENZA"].isna() # Find the index of NaT values
idx_DT_FINE_ASSISTENZA_is_NaT = df["DT_FINE_ASSISTENZA"].isna() # Find the index of NaT values
idx_DT_DECESSO_is_NaT = df["DT_DECESSO"].isna() # Find the index of NaT values
idx_DT_INGRESSO_FUP_is_NaT = df["DT_INGRESSO_FUP"].isna() # Find the index of NaT values
idx_DT_FINE_FUP_is_NaT = df["DT_FINE_FUP"].isna() # Find the index of NaT values
df["DISTURBO"] = df["DISTURBO"].astype(str) # Convert to string type
df["COORTE"] = df["COORTE"].astype(str) # Convert to string type
df["TOT_INTERVENTI"] = df["TOT_INTERVENTI"].astype(int) # Convert to string type
df["MESI_FUP"] = df["MESI_FUP"].astype(int)
idx_MESI_FUP_is_NaN = df["MESI_FUP"].isna() # Find the index of NaT values
idx_giorni_fup_is_NaN = df["giorni_fup"].isna() # Find the index of NaT values
idx_ALMENO_1_INT_is_NaN = df["ALMENO_1_INT"].isna()
df["ALMENO_1_INT"][idx_ALMENO_1_INT_is_NaN] = 0
df["ALMENO_1_INT"] = df["ALMENO_1_INT"].astype(int)
df["ALMENO_1_INT"] = df["ALMENO_1_INT"].astype(bool)



"""Roport:
ID_ASSISTITO is always defined and has zero missing values.
SESSO is always defined and has zero missing values.
DT_NASCITA has some missing values as NaT objects.
DT_INIZIO_ASSISTENZA has some missing values as NaT objects.
DT_FINE_ASSISTENZA has some missing values as NaT objects.
    This is quite understandable as some patients are still in care.
DT_DECESSO has some missing values as NaT objects.
    This is quite understandable as some patients are still alive.
DT_INGRESSO_FUP has some missing values as NaT objects.
DT_FINE_FUP has some missing values as NaT objects.
    This is quite understandable as some patients are still in care (?).
DISTURBO is always defined and has zero missing values.
COORTE is always defined as a string (a single char) and has zero missing values.
TOT_INTERVENTI is always defined and has zero missing values.
    It is mostly zero, but there are some patients with some up to a lot of interventions.
    This variable correlates perfectly with ALMENO_1_INT: where the latter is not a NaN, the former is always > 0.
    Thus, where ALMENO_1_INT is NaN, ALMENO_1_INT is set to False, else True.
MESI_FUP has no missing values, but it is alweays zero.
giorni_fup has only missing values (they are all NaN).
ALMENO_1_INT is NaN when TOT_INTERVENTI is zero, else it is 1.
    Can be converted to a boolean variable.
    sum(df["ALMENO_1_INT"]) == sum(df["TOT_INTERVENTI"] != 0)
"""

# Adding redundant yet useful colums to the dataframe
df["ANNO_NASCITA"] = df["DT_NASCITA"].dt.year
df["MESE_NASCITA"] = df["DT_NASCITA"].dt.month

# Convert all missing values to None
for column in df.columns:
    df[column] = df[column].where(pandas.notnull(df[column]), None)


###############################################
# View the columns
header_list = list(df.columns)
print("\n", header_list, "\n")

# Explore column by column
print(df[["COORTE", "TOT_INTERVENTI", "ALMENO_1_INT"]])
#print(df["ID_ASSISTITO"].describe())
print(sum(df["ALMENO_1_INT"]), sum(df["TOT_INTERVENTI"] != 0))

