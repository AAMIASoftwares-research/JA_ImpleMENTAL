import os, sys
import pandas
import matplotlib.pyplot as plt
#HoloViz libraries
import hvplot
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

# Dashboard
# https://holoviz.org/tutorial/index.html


# --------------- #

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
#hvplot.show(plot)

##################
# Simple Panel with example data
##################
import panel
panel.extension(
    'tabulator',
    template='material',
    sizing_mode='stretch_width'
)

ja_implemental_webpage_link = "https://ja-implemental.eu/about/"
title_md = "# JA ImpleMENTAL"
p_title_md = panel.pane.Markdown(title_md, width=250)

subtitle_md = """[JA ImpleMENTAL]({ja_implemental_webpage_link}) is a Joint Action (JA) co-funded by the European Commission (EC) under the Third Health Programme (2014-2020).
The JA ImpleMENTAL project aims to improve the quality of mental health care in Europe by identifying, analysing and exchanging good practices in mental health care."""
p_subtitle_md = panel.pane.Markdown(subtitle_md)

p_ja_implemental_logo_png = panel.pane.PNG(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/assets/ImpleMENTAL_logo_512x512.png",
    height=40,
    width=40
)
p_eu_funding_png = panel.pane.PNG(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/assets/en-co-funded-by-the-eu_pos.png",
    height=40
)

header = panel.Row(p_ja_implemental_logo_png, p_title_md)
header = panel.Row(
    header, p_eu_funding_png,
    styles=dict(background='WhiteSmoke'),
    height=60
)

#
# https://ja-implemental.eu/

header = panel.panel(
    """
    <div class="header-container-implemental"
    style="
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        width: 100vw;
        max-height: 311px;
        min-height: 310px;
        padding: 0;
        margin: 0;
        background: url('https://implemental.files.wordpress.com/2021/11/2000_podloga-s-logo.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: 50%;
        box-sizing: border-box;
    ">
        <h1 style="margin-left: 1.5em; font-style: normal; font-weight: 400; font-family: sans-serif; font-size:1.5em;">
            <a href="https://ja-implemental.eu/" style="text-decoration: none; color: black;">
                JA on Implementation of Best Practices in</br>
                the area of Mental Health
            </a>
        </h1>
        <img src="https://implemental.files.wordpress.com/2022/09/en-co-funded-by-the-eu_pos.png?w=300"
            alt="europe flag" style="float:right; margin-right: 1em;">
    </div>
    """,
    styles={
        "width": "100vw",
        "margin": "0",
        "padding": "0"
    }
)





tot_interventi_widget = panel.widgets.FloatSlider(name='Totale Interventi', start=5, end=40, value=10)

df2i = df2.interactive()
df2_filtered = df2i[df2i["TOT_INTERVENTI"] > tot_interventi_widget]

plot = df2_filtered.hvplot.scatter(
    x='TOT_INTERVENTI',
    y='ALMENO_1_INT',
    cnorm='eq_hist', 
    cmap='Reds',
    color="TOT_INTERVENTI",
    title='Scatter plot',
    responsive=True, height=500
)



body = panel.Column(
    plot,
    tot_interventi_widget
)

footer = p_subtitle_md

p = panel.Column(
    header,
    body,
    footer
)

p.show()

