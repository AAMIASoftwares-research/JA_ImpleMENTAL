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
        width: calc(100vw - 17px);
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
        "width": "calc(100vw - 17px)",
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
        width: calc(100vw - 17px);
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
        "margin": "0",
        "padding": "0",
        "position": "fixed",
        "bottom": "0"
    }
)












##################
# Open the dataset
##################

######    NOTE    #########
# here, everything has to be done again once we have true data
# as for now, we invent just to show that we ave something to show

FILE_NAME = "Indicatore 1_BIPO_coorteA.sas7bdat"
FILE = os.path.join(DATA_FOLDER, FILE_NAME)
df = read_sas_database_ind_1(FILE)

if 0:
    print(df.columns)

# bipo, ind 1, 2021

df["INDICATORE"] = "Indicatore 1"
df["ANNO_DI_INCLUSIONE"] = 2021

####### augment data
# ricreare un database verosimile seguendo le seguenti possibilita

choice_disturbo = ["BIPO", "SCHIZO", "DEPRE", "ADHD"]
choice_coorte = ["A", "B", "C", "D"]
choice_anno_di_inclusione = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
choice_indictore = ["Indicatore 1", "Indicatore 2", "Indicatore 3"]
choice_sex = ["M", "F"]*50 + [None]
choice_anno_nascita = [i for i in range(1950, 2005)] + [None]
choice_mese_nascita = [i for i in range(1,13)]
choice_mesi_fup = [i for i in range(1, 5*12)] + [None]

n_rows = 300000
df = pandas.DataFrame({
    # disturbo, coorte, anno inclusione, indicatore
    "DISTURBO": numpy.random.choice(choice_disturbo, n_rows, replace=True),
    "COORTE": numpy.random.choice(choice_coorte, n_rows, replace=True),
    "ANNO_DI_INCLUSIONE": numpy.random.choice(choice_anno_di_inclusione, n_rows, replace=True),
    "INDICATORE": numpy.random.choice(choice_indictore, n_rows, replace=True),
    # anagrafe assistito
    "ID_ASSISTITO": numpy.random.choice([i for i in range(1, 1000000)], n_rows, replace=False),
    "SESSO": numpy.random.choice(choice_sex, n_rows, replace=True),
    "ANNO_NASCITA": numpy.random.choice(choice_anno_nascita, n_rows, replace=True),
    "MESE_NASCITA": numpy.random.choice(choice_mese_nascita, n_rows, replace=True),
    # ... (manca roba)
    # anagrafe assistenza
    "MESI_FUP": numpy.random.choice(choice_mesi_fup, n_rows, replace=True),
    # ... (manca roba)
    # numero interventi
    "TOT_INTERVENTI": numpy.random.choice([i for i in range(1, 150)]+[None], n_rows, replace=True)
})
# Dove anno nascita è None, anche mese nascita deve essere none
df["ANNO_NASCITA"].where(df["MESE_NASCITA"] != None, None,  inplace = True)
df["MESE_NASCITA"].where(df["ANNO_NASCITA"] != None, None,  inplace = True)





################
# All diseases page
################

map_disturbi = {
    "ALL": "All diseases",
    "BIPO": "Bipolar Disorder",
    "SCHIZO": "Schizophrenia",
    "DEPRE": "Depression",
    "ADHD": "Attention Deficit Hyperactivity Disorder"
}

# - for each coorte, plot the number of patients by year of inclusion, for all diseases and for each disease

def plot_all_diseases_by_year_of_inclusion(df: pandas.DataFrame, coorte="Coorte A"):
    #
    # attenzione: non cinsidera i doppioni, nel senso che, una persona può comparire nella
    # indicatore 1, o 2, o n, e quindi essere contata più volte.
    # Funzione prettamente esemplare e d'esercizio.
    #
    # select all by coorte
    if coorte is None:
        df2 = df[["DISTURBO", "ANNO_DI_INCLUSIONE"]].copy()
    else: 
        coorte = coorte.upper()[-1]
        df2 = df.loc[df["COORTE"] == coorte, ["DISTURBO", "ANNO_DI_INCLUSIONE"]].copy()
    # for each year of inclusion, create a tuple (disturbo, count)
    year_of_inclusion_list = list(set(df2["ANNO_DI_INCLUSIONE"]))
    year_of_inclusion_list.sort()
    disturbi = list(set(df2["DISTURBO"]))
    disturbi.sort()
    disturbi = numpy.insert(disturbi, 0, "ALL")
    rows_to_add = []
    for y in year_of_inclusion_list:
        row_ = []
        for dist in disturbi:
            if dist == "ALL":
                c_= len(df2.loc[df2["ANNO_DI_INCLUSIONE"] == y, :])
            else:
                c_ = len(df2.loc[(df2["ANNO_DI_INCLUSIONE"] == y) & (df2["DISTURBO"] == dist), :])
            row_.append(c_)
        rows_to_add.append(row_)
    rows_to_add = numpy.array(rows_to_add)
    rows_to_add = numpy.insert(rows_to_add, 0, year_of_inclusion_list, axis=1)
    columns = ["ANNO DI INCLUSIONE"]
    columns.extend([map_disturbi[d] for d in disturbi])
    df3 = pandas.DataFrame(
        rows_to_add,
        index=year_of_inclusion_list,
        columns=columns
    )
    # x: always the year of inclusion
    # y: the number of patient stratified by disease
    df3.drop(columns=[map_disturbi["ALL"]], inplace=True)
    pl = df3.hvplot.bar(
        x="ANNO DI INCLUSIONE",
        y=[map_disturbi[d] for d in disturbi[1:]],
        stacked=True,
        xlabel="Anno di inclusione",
        ylabel="Numero di pazienti",
        title="Numero di pazienti per anno di inclusione, per disturbo.",
        legend="top_left",
        max_width=600
    )
    if 0:
        hvplot.show(pl)
    else:
        return pl


#plot_all_diseases_by_year_of_inclusion(df)

def plot_all_diseases_by_year_of_inclusion_binding_coorte(coorte="Coorte A"):
    return plot_all_diseases_by_year_of_inclusion(df, coorte=coorte)







##################
# Dashboard
##################

# - TITLE AND DISEASE SELECTOR
title_choice_map = {
    "Overview on all diseases": "Overview on all diseases",
    "Schizophrenia": "Schizophrenia",
    "Bipolar Disorder": "Bipolar Disorder",
    "Depression": "Depression"
}

if not df is None:
    disturbi = list(set(df["DISTURBO"]))
    disturbi.sort()
    disturbi = numpy.insert(disturbi, 0, "ALL")
    title_choice_map = {map_disturbi[k]: map_disturbi[k] for k in disturbi}

title_menu_items = [(k, v) for k, v in title_choice_map.items()]

title_menu_button = panel.widgets.MenuButton(
    name='Select Disease',
    items=title_menu_items,
    button_type='warning',
    max_width=300,
    min_width=150,
    styles={
        "margin-right": "2em"
    } 
)

title_menu_button.param.set_param(clicked=title_menu_items[0][0])

def disease_selector_row_title_maker(value):
    if value is None:
        value = """<span style="font-size: 1.1em; color: #888888ff;">
                Select a disease from the dropdown menu on the right.
                </span>"""
    if value == "All diseases":
        value = "Overview on all diseases"
    text = "<h1>"+value+"</h1>"
    html_pane = panel.pane.HTML(
        text,
        styles={
            "margin-left": "1.5em"
        }
    )
    return html_pane

disease_selector_row = panel.FlexBox(
    panel.bind(disease_selector_row_title_maker, title_menu_button.param.clicked), # 
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

top_selector_row = panel.Column(
    disease_selector_row,
    coorte_selector_row,
    styles={
        "margin-top": "0px",
        "padding-top": "0px",
        "margin-bottom": "5px",
        "background": "#e9ecefff",
        "border-radius": "16px"
    }
)


# - PLOTS AND VIXs

def get_main_box_elements(disease_selector_value):
    if disease_selector_value == "All diseases":
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion_binding_coorte, coorte_radio_group.param.value)
        ]
    else:
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion_binding_coorte, coorte_radio_group.param.value),
            plot_all_diseases_by_year_of_inclusion(df),
            plot_all_diseases_by_year_of_inclusion(df),
            plot_all_diseases_by_year_of_inclusion(df),
            plot_all_diseases_by_year_of_inclusion(df)
        ]
    
main_box = panel.GridBox(
    objects=panel.bind(get_main_box_elements, title_menu_button.param.clicked),
    ncols = 2,
    width_policy = "max",
    height_policy = "fit",
    align="center",
    styles={
        "justify-content": "space-evenly",
        "width": "95%"
    }
)




# - BODY

body = panel.Column(
    top_selector_row,
    main_box,
    styles={
        "margin-top": "20px",
        "padding-top": "0px",
        "margin-bottom": "15px"
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
        "background": "#ffffffff",
        "width": 'calc(100vw - 17px)',
        "height": "100%"
    }
)
p.show()