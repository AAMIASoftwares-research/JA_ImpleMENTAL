import os, sys
import pandas
import matplotlib.pyplot as plt
#HoloViz libraries
import hvplot.pandas
import holoviews
import bokeh
# Add backend extensions
#hvplot.extension('matplotlib')
# select matplotlib as the backend to use instead of bokeh
# All methods to show the plots must be changed accordingly
#if 0: 
#    hvplot.output(backend='matplotlib')


##################
# DIRECTORIES
##################

DATA_FOLDER = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/"
)
FILE_NAME = "Indicatore 1_BIPO_coorteA.sas7bdat"

FILE = os.path.join(DATA_FOLDER, FILE_NAME)

##################
# Open the dataset
##################
df = pandas.read_sas(FILE)

################
# Pre-processing
################
# Data type cleaning
# DateTime variables are already in datetime format
df["ID_ASSISTITO"] = df["ID_ASSISTITO"].astype(int)
df["SESSO"] = df["SESSO"].astype(str)
df["DISTURBO"] = df["DISTURBO"].astype(str)
df["COORTE"] = df["COORTE"].astype(str)
df["TOT_INTERVENTI"] = df["TOT_INTERVENTI"].astype(int)
df["MESI_FUP"] = df["MESI_FUP"].astype(int)
df["giorni_fup"].where(df["giorni_fup"].notnull(), -1,  inplace = True)
df["giorni_fup"] = df["giorni_fup"].astype(int)
df["giorni_fup"].where(df["giorni_fup"] != -1, None,  inplace = True)
df["ALMENO_1_INT"].where(df["ALMENO_1_INT"].notnull(), 0,  inplace = True)
df["ALMENO_1_INT"] = df["ALMENO_1_INT"].astype(int).astype(bool)

# Adding redundant yet useful colums to the dataframe
df["ANNO_NASCITA"] = df["DT_NASCITA"].dt.year
df["MESE_NASCITA"] = df["DT_NASCITA"].dt.month

# Convert all missing values to None for consistency
for column in df.columns:
    df[column] = df[column].where(pandas.notnull(df[column]), None)



##################
# Data exploration
##################
# https://holoviz.org/tutorial/Plotting.html

df2 = df[["TOT_INTERVENTI", "ALMENO_1_INT"]].copy()
df2["ALMENO_1_INT"] = df2["ALMENO_1_INT"].astype(int)

plot = df2.hvplot.scatter(
    x='TOT_INTERVENTI',
    y='ALMENO_1_INT',
    #rasterize=True, # Good just for very dense data
    cnorm='eq_hist', 
    cmap='Reds',
    title='Scatter plot'
)
hvplot.show(plot)