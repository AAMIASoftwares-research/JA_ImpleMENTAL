import os, sys
import pandas
import numpy
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
        border-radius: 0px 0px 16px 16px;
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
        <img src="https://implemental.files.wordpress.com/2022/09/en-co-funded-by-the-eu_pos.png?w=300"
             alt="europe flag"
             style="
                float:right;
                margin-right: 1em;
                max-width: 300px;
                min-width: 200px;
        ">
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
        border: solid 1px #555555;
        border-bottom: none;
        margin-left: -1px;
        margin-right: -1px;
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

# augment dataset so you have something to show

print(df.columns)


######### HOW To STRATIFY??? BOOOH HO POCHISSIMI DATI



##################
# Dashboard
##################

# - TITLE AND DISEASE CHOICE
title_choice_map = {
    "Overview on all diseases": "Overview on all diseases",
    "Schizophrenia": "Schizophrenia",
    "Bipolar Disorder": "Bipolar Disorder",
    "Depression": "Depression"
}

title_menu_items = [(k, v) for k, v in title_choice_map.items()]

title_menu_button = panel.widgets.MenuButton(
    name='Select Disease',
    items=title_menu_items,
    button_type='warning'
)

disease_selector_row_title = panel.pane.HTML(
    "<h1>"+title_menu_items[0][0]+"</h1>",
    styles={
        "margin-left": "1em"
    }
)

def disease_selector_row_title_callback(event):
    if not event.new == event.old:
        disease_selector_row_title.object = "<h1>"+event.new+"</h1>"

title_menu_button.on_click(disease_selector_row_title_callback)

disease_selector_row = panel.FlexBox(
    disease_selector_row_title, 
    title_menu_button,
    flex_direction="row",
    flex_wrap="nowrap", 
    align_content="center", # like justify content but vertically
    justify_content="space-around",  # like align content but horizontally
    align_items="center", # vertical align
    styles={}
)

# - COORTE CHOICE

coorte_explain_dict = {
    "Coorte A": "La \"coorte prevalente\" trattata è costituita da tutti i beneficiari del Servizio Sanitario Nazionale (SSN) residenti in una data regione che, nell'anno di inclusione, hanno avuto un contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
    "Coorte B": "La \"coorte dei nuovi pazienti presi in carico\" (o incidenti) è costituita dalla porzione della coorte prevalente che, nei due anni precedenti l'anno di inclusione, non ha sperimentato alcun contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
    "Coorte C": "La \"coorte dei nuovi casi presi in carico con disturbo all'esordio\" è costituita dalla porzione della coorte dei nuovi casi presi in carico che, nell'anno di inclusione, ha un'età inferiore o uguale ai 25 anni compiuti.",
    "Coorte D": "La \"coorte dei pazienti dimessi da ricovero in Servizio Psichiatrico di Diagnosi e Cura\" (SPDC) è costituita dalla porzione della coorte prevalente trattata che nell'anno di inclusione ha sperimentato almeno un ricovero in un Servizio SPDC o altre strutture psichiatriche per eventi acuti."
}

coorte_button_options_list = [
    k_ for k_, v_ in coorte_explain_dict.items()
]

coorte_radio_group = panel.widgets.RadioButtonGroup(
    name='coorte selector', 
    options=coorte_button_options_list, 
    value=coorte_button_options_list[0],
    button_type='primary'
)

def build_coorte_tooltip_html(text: str):
    s_ = """
        <p style="
            color: #888888ff;
            font-size: 0.9em;
            text-align: center;
        ">
    """
    e_ = "</p>"
    text = text.replace("\"", """<span style='color:#707070ff;'><b>""", 1)
    text = text.replace("\"", """</b></span>""", 1)
    return s_ + text + e_

def update_coorte_html(value):
    return panel.pane.HTML(build_coorte_tooltip_html(coorte_explain_dict[value]))

coorte_selector_row = panel.Column(
    coorte_radio_group,
    panel.bind(update_coorte_html, coorte_radio_group.param.value)
)


# - BODY

body = panel.Column(
    disease_selector_row,
    coorte_selector_row,
    styles={
        #"padding": "5px",
        #"margin": "5px",
        "margin-top": "20px",
        "padding-top": "0px",
        "margin-bottom": "10px",
        "background": "#e9ecefff",
        "border-radius": "16px"
    }
)

##################
# Dashboard
##################

p = panel.Column(
    header,
    body,
    footer,
    styles={
        "background": '#f5f5f5ff',
        "width": '100vw',
        "height": "100%"
    }
)
p.show()