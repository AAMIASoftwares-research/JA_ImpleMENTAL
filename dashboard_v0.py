import os, sys
import pandas
import matplotlib.pyplot as plt
#HoloViz libraries
import hvplot
import hvplot.pandas
import holoviews
import bokeh
# Add backend extensions
# select matplotlib as the backend to use instead of bokeh
# All methods to show the plots must be changed accordingly
if 0: 
    hvplot.extension('matplotlib')
    hvplot.output(backend='matplotlib')

import panel
panel.extension(
    'tabulator',
    template='material',
    sizing_mode='stretch_width'
)

from .sas_database_reader import read_sas_database_ind_1

##################
# DIRECTORIES
##################

DATA_FOLDER = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/"
)


########
# header
########

# https://ja-implemental.eu/
header = panel.panel(
    """
    <div class="header-container-implemental" style="
        display: flex;
        flex-direction: row;
        justify-content: space-evenly;
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
        <h1 style="
            margin-right: 1.5em;
            font-style: normal;
            font-weight: 600;
            font-family: sans-serif;
            font-size: 1.1em;
            direction: ltr;
            background-color: #e7e7e7;
            border-radius: 8px;
            padding: 5px;
            text-align: center;
            color: #333333;
            border: solid 1px #555555;
            ">
            <a href="https://ja-implemental.eu/" style="text-decoration: none;color: inherit;">
                JA on Implementation of Best Practices in<br>
                the area of Mental Health
            </a>
        </h1>
        <img src="https://implemental.files.wordpress.com/2022/09/en-co-funded-by-the-eu_pos.png?w=300" alt="europe flag" style="float:right; margin-right: 1em;">
    </div>
    """,
    styles={
        "width": "100vw",
        "margin": "0",
        "padding": "0"
    }
)


########
# footer
########

footer = panel.panel(
    """
    <div class="footer-container-implemental" style="
        margin: auto;
        width: 100vw;
        text-align: center;
        margin-top: -16px;
        margin-bottom: 0%;
        background-color: #e9ecef;
        border-radius: 16px 16px 0px 0px;
        ">
        <p style="
            display: inline-block;
            font-size: 0.85em;
            color: #546e7a;
        ">
            JA ImpleMENTAL is a Joint Action (JA) co-funded by the European Commission (EC)
            under the Third Health Programme (2014-2020). <br>
            The JA ImpleMENTAL project aims to improve the quality of mental health care in
            Europe by identifying, analysing and exchanging good practices in mental health care.
        </p>
    </div>
    """,
    styles={
        "width": "100vw",
        "margin": "0",
        "padding": "0",
        "position": "fixed",
        "bottom": "0"
    }
)



##################
# Open the dataset
##################

FILE_NAME = "Indicatore 1_BIPO_coorteA.sas7bdat"
FILE = os.path.join(DATA_FOLDER, FILE_NAME)
df = read_sas_database_ind_1(FILE)


######### HOW T STRATIFY??? BOOOH HO POCHISSIMI DATI






##################
# Dashboard
##################

p = panel.Column(
    header,
    footer
)
p.show()