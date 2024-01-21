# Author: Matteo Leccardi
# Interesting resources:
# https://justinbois.github.io/bootcamp/2022/lessons/l40_holoviews.html


import os, sys
import pandas
import numpy
import matplotlib.pyplot as plt
#HoloViz libraries
import hvplot
import hvplot.pandas
import holoviews
import bokeh

import panel
panel.extension(
    'tabulator',
    template='material',
    sizing_mode='stretch_width'
)

from .sas_database_reader import read_sas_database_ind_1

############
# UTILITIES
############

def dict_find_key_by_value(d, v):
    for k in d.keys():
        if d[k] == v:
            return k
    return None

##############
# DIRECTORIES
##############

DATA_FOLDER = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/"
)





###################
# Open the dataset
###################

######    NOTE    #########
# here, everything has to be done again once we have true data.
# The developed pipeline opens and cleans the data a little bit,
# however this is not final, as the final data structure and specifications
# of the database is to yet defined.

FILE_NAME = "Indicatore 1_BIPO_coorteA.sas7bdat"
FILE = os.path.join(DATA_FOLDER, FILE_NAME)
DB = read_sas_database_ind_1(FILE)

if 0:
    print(DB.columns)

# bipo, ind 1, 2021

DB["INDICATORE"] = "Indicatore 1"
DB["ANNO_DI_INCLUSIONE"] = 2021




############################
# DUMMY DATASET FOR TESTING
############################
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
DB = pandas.DataFrame({
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
    "TOT_INTERVENTI": numpy.random.poisson(2, n_rows) # indicatore si calcola con questo
})
# Dove anno nascita is None, anche mese nascita deve essere none
DB.loc[DB["MESE_NASCITA"].isnull(), "ANNO_NASCITA"] = None
DB.loc[DB["ANNO_NASCITA"].isnull(), "MESE_NASCITA"] = None
# Cambia TOT_INTERVENTI in base a indicatore, così da avere grafici un po diversi
DB.loc[DB["INDICATORE"] == "Indicatore 1", "TOT_INTERVENTI"] = (DB.loc[DB["INDICATORE"] == "Indicatore 1", "TOT_INTERVENTI"] - 1).clip(lower=0)
DB.loc[DB["INDICATORE"] == "Indicatore 2", "TOT_INTERVENTI"] = (DB.loc[DB["INDICATORE"] == "Indicatore 2", "TOT_INTERVENTI"] - 2).clip(lower=0)
# Dove TOT_INTERVENTI is 0, qualche volta lo mettiamo come None o NaN, così il codice a valle risulta piu robusto
DB["TOT_INTERVENTI"] = DB["TOT_INTERVENTI"].astype(float) # first i have to cast it, otherwise pandas is not happy
DB.loc[DB["TOT_INTERVENTI"] == 0, "TOT_INTERVENTI"] = numpy.random.choice(
    [0, numpy.nan, numpy.nan, numpy.nan], len(DB.loc[DB["TOT_INTERVENTI"] == 0, "TOT_INTERVENTI"]),
    replace=True
)




# preliminary database cleaning
# - the following steps should be put into a proper function, nut as of now, i'll do that here
# - - Replace None and numpy.nan with 0
DB["TOT_INTERVENTI"].fillna(0, inplace=True)
# - - Convert back to integer
DB["TOT_INTERVENTI"] = DB["TOT_INTERVENTI"].astype(int)




#####################
# LANGUAGE SELECTION 
#####################


# make a dropdown menu and related binding callback
# so that languace can be changed easily by the user

LANGUAGE_DICT = {
    # The options parameter also accepts a dictionary
    # whose keys are going to be the labels of the dropdown menu,
    # while the values are the objects that will be set into the 
    # widget.value parameter field.
    "Deutsch" : "de",
    "English" : "en",
    "Español" : "es",
    "Français" : "fr",
    "Italiano" : "it",
    "Português" : "pt"
}
DEFAULT_LANGUAGE = "en"

AVAILABLE_LANGUAGES = [v for v in LANGUAGE_DICT.values()]
display_language = DEFAULT_LANGUAGE ########################## back-compatible with the code

def language_selector_widget_make_name(language_code):
    return "Language - " + dict_find_key_by_value(LANGUAGE_DICT, language_code)

language_selector_widget = panel.widgets.Select(
    name=language_selector_widget_make_name(DEFAULT_LANGUAGE),
    value=DEFAULT_LANGUAGE,
    options=LANGUAGE_DICT,
    width=120,
    styles={
        "position": "absolute",
        "margin-top": "0.5em",
        "margin-left": "5.5em",
    }
)

def language_selector_widget_update_name_callback(event):
    language_selector_widget.name = language_selector_widget_make_name(event.new)

language_selector_widget.param.watch(
    language_selector_widget_update_name_callback, 
    'value'
)

# This widget still has no effect on the dashboard.
# So, it is not displayed. It is still unclear if by changing language
# through this widget, it is really possible to change language of everything
# on the fly, or if it is necessary or much easier to reload the page.





#########
# HEADER
#########

title_str_html = {
    "en": "JA on Implementation of Best Practices </br> in the area of Mental Health",
    "it": "JA sull'implementazione delle migliori pratiche </br> nel campo della salute mentale",
    "fr": "JA sur la mise en œuvre des meilleures pratiques </br> dans le domaine de la santé mentale",
    "de": "JA zur Umsetzung bewährter Verfahren im Bereich </br> der psychischen Gesundheit",
    "es": "JA sobre la implementación de las mejores prácticas </br> en el ámbito de la salud mental",
    "pt": "JA sobre a implementação das melhores práticas </br> no domínio da saúde mental",
}

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
                """ + title_str_html[display_language] + """
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


#########
# FOOTER
#########

footer_str_html = {
    "en": """JA ImpleMENTAL is a Joint Action (JA) co-funded by the European Commission (EC)
                under the Third Health Programme (2014-2020). </br>
                The JA ImpleMENTAL project aims to improve the quality of mental health care in
                Europe by identifying, analysing and exchanging good practices in mental health care.""",
    "it": """JA ImpleMENTAL è un'azione congiunta (JA) cofinanziata dalla Commissione europea (CE)
                nell'ambito del terzo programma sanitario (2014-2020). </br>
                Il progetto JA ImpleMENTAL mira a migliorare la qualità dell'assistenza sanitaria
                mentale in Europa identificando, analizzando e scambiando buone pratiche nell'assistenza
                sanitaria mentale.""",
    "fr": """JA ImpleMENTAL est une action conjointe (JA) cofinancée par la Commission européenne (CE)
                dans le cadre du troisième programme de santé (2014-2020). </br>
                Le projet JA ImpleMENTAL vise à améliorer la qualité des soins de santé mentale en Europe
                en identifiant, analysant et échangeant les bonnes pratiques en matière de soins de santé
                mentale.""",
    "de": """JA ImpleMENTAL ist eine Joint Action (JA), die von der Europäischen Kommission (EK)
                im Rahmen des Dritten Gesundheitsprogramms (2014-2020) kofinanziert wird. </br>
                Das Projekt JA ImpleMENTAL zielt darauf ab, die Qualität der psychischen Gesundheitsversorgung in Europa
                durch die Identifizierung, Analyse und den Austausch bewährter Praktiken </br>
                in der psychischen Gesundheitsversorgung zu verbessern.""",
    "es": """JA ImpleMENTAL es una Acción Conjunta (JA) cofinanciada por la Comisión Europea (CE)
                en el marco del Tercer Programa de Salud (2014-2020). </br>
                El proyecto JA ImpleMENTAL tiene como objetivo mejorar la calidad de la atención de salud mental en Europa
                mediante la identificación, el análisis y el intercambio de buenas prácticas en la atención de salud mental.""",
    "pt": """JA ImpleMENTAL é uma Ação Conjunta (JA) cofinanciada pela Comissão Europeia (CE)
                no âmbito do Terceiro Programa de Saúde (2014-2020). </br>
                O projeto JA ImpleMENTAL tem como objetivo melhorar a qualidade do atendimento de saúde mental na Europa
                identificando, analisando e trocando boas práticas no atendimento de saúde mental."""
}

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
            """ + footer_str_html[display_language] + """
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













####################
# All diseases page
####################

diseases_map = {
    "en": {
        "ALL": "All diseases",
        "BIPO": "Bipolar Disorder",
        "SCHIZO": "Schizophrenia",
        "DEPRE": "Depression",
        "ADHD": "Attention Deficit Hyperactivity Disorder"
    },
    "it": {
        "ALL": "Tutti i disturbi",
        "BIPO": "Disturbo bipolare",
        "SCHIZO": "Schizofrenia",
        "DEPRE": "Depressione",
        "ADHD": "Disturbo da deficit di attenzione e iperattività"
    },
    "fr": {
        "ALL": "Tous les troubles",
        "BIPO": "Trouble bipolaire",
        "SCHIZO": "Schizophrénie",
        "DEPRE": "Dépression",
        "ADHD": "Trouble du déficit de l'attention avec hyperactivité"
    },
    "de": {
        "ALL": "Alle Störungen",
        "BIPO": "Bipolare Störung",
        "SCHIZO": "Schizophrenie",
        "DEPRE": "Depression",
        "ADHD": "Aufmerksamkeitsdefizit-Hyperaktivitätsstörung"
    },
    "es": {
        "ALL": "Todos los trastornos",
        "BIPO": "Trastorno bipolar",
        "SCHIZO": "Esquizofrenia",
        "DEPRE": "Depresión",
        "ADHD": "Trastorno por déficit de atención con hiperactividad"
    },
    "pt": {
        "ALL": "Todos os distúrbios",
        "BIPO": "Transtorno bipolar",
        "SCHIZO": "Esquizofrenia",
        "DEPRE": "Depressão",
        "ADHD": "Transtorno de déficit de atenção com hiperatividade"
    }
}

database_keys_map = {
    "en": {
        "DISTURBO": "Disease",
        "COORTE": "Cohort",
        "ANNO_DI_INCLUSIONE": "Year of inclusion",
        "INDICATORE": "Indicator",
        "ID_ASSISTITO": "Patient ID",
        "SESSO": "Biological sex",
        "ANNO_NASCITA": "Year of birth",
        "MESE_NASCITA": "Month of birth",
        "MESI_FUP": "Months of follow up",
        "TOT_INTERVENTI": "Number of interventions"
    },
    "it": {
        "DISTURBO": "Disturbo",
        "COORTE": "Coorte",
        "ANNO_DI_INCLUSIONE": "Anno di inclusione",
        "INDICATORE": "Indicatore",
        "ID_ASSISTITO": "ID Assistito",
        "SESSO": "Sesso",
        "ANNO_NASCITA": "Anno di nascita",
        "MESE_NASCITA": "Mese di nascita",
        "MESI_FUP": "Mesi di follow up",
        "TOT_INTERVENTI": "Numero di interventi"
    },
    "fr": {
        "DISTURBO": "Trouble",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Année d'inclusion",
        "INDICATORE": "Indicateur",
        "ID_ASSISTITO": "ID Patient",
        "SESSO": "Sexe",
        "ANNO_NASCITA": "Année de naissance",
        "MESE_NASCITA": "Mois de naissance",
        "MESI_FUP": "Mois de suivi",
        "TOT_INTERVENTI": "Nombre d'interventions"
    },
    "de": {
        "DISTURBO": "Störung",
        "COORTE": "Kohorte",
        "ANNO_DI_INCLUSIONE": "Jahr der Aufnahme",
        "INDICATORE": "Indikator",
        "ID_ASSISTITO": "Patienten-ID",
        "SESSO": "Geschlecht",
        "ANNO_NASCITA": "Geburtsjahr",
        "MESE_NASCITA": "Geburtsmonat",
        "MESI_FUP": "Monate der Nachverfolgung",
        "TOT_INTERVENTI": "Anzahl der Interventionen"
    },
    "es": {
        "DISTURBO": "Trastorno",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Año de inclusión",
        "INDICATORE": "Indicador",
        "ID_ASSISTITO": "ID del paciente",
        "SESSO": "Sexo",
        "ANNO_NASCITA": "Año de nacimiento",
        "MESE_NASCITA": "Mes de nacimiento",
        "MESI_FUP": "Meses de seguimiento",
        "TOT_INTERVENTI": "Número de intervenciones"
    },
    "pt": {
        "DISTURBO": "Distúrbio",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Ano de inclusão",
        "INDICATORE": "Indicador",
        "ID_ASSISTITO": "ID do paciente",
        "SESSO": "Sexo",
        "ANNO_NASCITA": "Ano de nascimento",
        "MESE_NASCITA": "Mês de nascimento",
        "MESI_FUP": "Meses de acompanhamento",
        "TOT_INTERVENTI": "Número de intervenções"
    }
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
    columns = [database_keys_map[display_language]["ANNO_DI_INCLUSIONE"]]
    columns.extend([diseases_map[display_language][d] for d in disturbi])
    df3 = pandas.DataFrame(
        rows_to_add,
        index=year_of_inclusion_list,
        columns=columns
    )
    # x: always the year of inclusion
    # y: the number of patient stratified by disease
    y_abels_map = {
        "en": "Number of patients",
        "it": "Numero di pazienti",
        "fr": "Nombre de patients",
        "de": "Anzahl der Patienten",
        "es": "Número de pacientes",
        "pt": "Número de pacientes"
    }
    plot_title_map = {
        "en": "Number of patients by year of inclusion, stratified by disease.",
        "it": "Numero di pazienti per anno di inclusione, stratificati per disturbo.",
        "fr": "Nombre de patients par année d'inclusion, stratifiés par maladie.",
        "de": "Anzahl der Patienten nach Jahr der Aufnahme, stratifiziert nach Krankheit.",
        "es": "Número de pacientes por año de inclusión, estratificados por enfermedad.",
        "pt": "Número de pacientes por ano de inclusão, estratificados por doença."
    }
    df3.drop(columns=[diseases_map[display_language]["ALL"]], inplace=True)
    """pl = df3.hvplot.bar(
        x=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
        y=[diseases_map[display_language][d] for d in disturbi[1:]],
        stacked=True,
        xlabel=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
        ylabel=y_abels_map[display_language],
        title=plot_title_map[display_language],
        legend="top_left",
        max_width=600
    )"""
    # now, we create the overall plot
    # - first, the plot of the number of all patients
    df3_for_plotting = df3.copy()
    df3_for_plotting[y_abels_map[display_language]] = df3_for_plotting[[diseases_map[display_language][d] for d in disturbi[1:]]].sum(axis=1)
    df3_for_plotting = df3_for_plotting.drop(columns=[diseases_map[display_language][d] for d in disturbi[1:]])
    PLOT_COLOR = "blue"
    curve = holoviews.Curve(
        data=df3_for_plotting,
        kdims=[database_keys_map[display_language]["ANNO_DI_INCLUSIONE"]],
        vdims=[y_abels_map[display_language]],
    ).opts(
        color=PLOT_COLOR,
        line_width=1.5
    )
    scatter = holoviews.Scatter(
        data=df3_for_plotting,
        kdims=[database_keys_map[display_language]["ANNO_DI_INCLUSIONE"]],
        vdims=[y_abels_map[display_language]],
    ).opts(
        size=10,  # size of the marker
        fill_color='white',  # color inside the marker
        line_color=PLOT_COLOR,  # color of the marker's edge
        line_width=1.5,  # thickness of the marker's edge,
        tools=["hover"]
    )
    text_labels = holoviews.Labels(
        {
            ('x', 'y'): df3_for_plotting, 
            'text': [str(a) for a in df3_for_plotting[y_abels_map[display_language]]]
        }, 
        ['x', 'y'], 'text'
    ).opts(
        align="center",
        text_font_size='8pt',
        yoffset = max(df3_for_plotting[y_abels_map[display_language]])/10,
        text_color="#302070"
    )
    # - here, the barplot with the stacked subdivisions
    df3_melted = pandas.melt(
        df3, 
        id_vars=[database_keys_map[display_language]["ANNO_DI_INCLUSIONE"]],
        value_vars=[diseases_map[display_language][d] for d in disturbi[1:]],
        var_name=disease_word_langauges_map[display_language],
        value_name=y_abels_map[display_language]
    )
    bars = holoviews.Bars(
        data=df3_melted,
        kdims=[database_keys_map[display_language]["ANNO_DI_INCLUSIONE"], disease_word_langauges_map[display_language]],
        vdims=[y_abels_map[display_language]],
    ).opts(
        stacked=True,
        legend_position="bottom_left",
        tools=["hover"],
        
    )
    # - composite plot
    plot = (bars * curve * scatter * text_labels).opts(
        xlabel=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
        ylabel=y_abels_map[display_language],
        title=plot_title_map[display_language],
        ylim=(
            0, 
            (5/4)*df3_for_plotting[y_abels_map[display_language]].max()
        )
    )
    return plot








######################
# Single disease page
######################

# - depending on the selected disease, cohort, and indicator, plot
# the history (by year of inclusion on the x axis) of the number of patients
# Also stratify the patients by sex and age (in 5 years intervals)

def clean_global_dataframe_by_disease_cohort_indicator(df_global, disease, cohort, indicator):
    """
    This function takes the global dataframe and returns a new dataframe
    with only the rows that are relevant to the selected disease, cohort, and indicator.
    """
    df = df_global.loc[
        (df_global["DISTURBO"] == disease) &
        (df_global["COORTE"] == cohort) &
        (df_global["INDICATORE"] == indicator),
        ["ANNO_DI_INCLUSIONE", "SESSO", "ANNO_NASCITA", "MESE_NASCITA", "TOT_INTERVENTI"]
    ].copy()
    # add age column
    df.loc[df["MESE_NASCITA"].isna(), "MESE_NASCITA"] = 9 # if month of birth is unknown, assume september
    df["AGE"] = df["ANNO_DI_INCLUSIONE"] - df["ANNO_NASCITA"]
    df.loc[df["MESE_NASCITA"] <= 11, "AGE"] -= 1
    # remove year of birth and month of birth
    df.drop(columns=["ANNO_NASCITA", "MESE_NASCITA"], inplace=True)
    # clean TOT_INTERVENTI from NaN
    df.loc[df["TOT_INTERVENTI"].isna(), "TOT_INTERVENTI"] = 0
    # clean SESSO from NaN and None and subtitute with "Unk."
    df.loc[df["SESSO"].isna(), "SESSO"] = "Unk."
    # clean AGE from NaN and None and subtitute with "Unk."
    df.loc[df["AGE"].isna(), "AGE"] = "Unk."
    # return the cleaned dataframe
    return df

# now basically I have to create a function which outputs a row of the body of the dashboard
# given:
# - the global dataframe
# - the disease
# - the cohort
# - the indicator

def get_clean_dataframe_filters_for_numerator_and_denominator(df, year_of_inclusion:int, sex:str, age_range: tuple[int, int], age_range_min_max: tuple[int, int]):
    # denominator
    # - year of inclusion
    denominator_condition = df["ANNO_DI_INCLUSIONE"] == year_of_inclusion
    # - age range
    if age_range[0] == age_range_min_max[0] and age_range[1] == age_range_min_max[1]:
        # in this case, the user is asking for all ages, so we give them also the unknowns
        # in other words, we remove nothing from the denominator (we keep all the people)
        pass 
    else:
        # in this case, the unknowns are not considered in the indicator calculation
        age_vector = numpy.array([(int(a) if len(str(a))<4 else -10) for a in df["AGE"] ])
        denominator_condition = denominator_condition & (age_vector >= age_range[0]) & (age_vector <= age_range[1])
    # - biological sex
    if sex == "ALL":
        pass
    elif sex == "M":
        denominator_condition = denominator_condition & (df["SESSO"] == "M")
    elif sex == "F":
        denominator_condition = denominator_condition & (df["SESSO"] == "F")
    elif sex == "M and F":
        denominator_condition = denominator_condition & ((df["SESSO"] == "M") | (df["SESSO"] == "F"))
    elif sex == "Unk.":
        pass
    # numerator
    denominator_condition = numpy.array(denominator_condition)
    numerator_condition = denominator_condition.copy()
    if sex == "Unk.":
        numerator_condition = numerator_condition & (df["SESSO"] == "Unk.")
    numerator_condition = numerator_condition & (df["TOT_INTERVENTI"] > 0)
    return numerator_condition, denominator_condition


def get_plot__binding_callback(df_clean, sex_selector_widget, age_range_selector_widget, age_range_min_max):
        # make a plot with x: year of inclusion, y: indicator value, considering the provided stratification
        # simple version: just a plot
        x = [int(y) for y in list(set(df_clean["ANNO_DI_INCLUSIONE"]))]
        x.sort()
        y = []
        for year in x:
            numerator, denominator = (numpy.sum(a) for a in get_clean_dataframe_filters_for_numerator_and_denominator(df_clean, year, sex_selector_widget, age_range_selector_widget, age_range_min_max))
            if denominator == 0:
                y.append(0)
            else:
                y.append(numerator / denominator)
        # make the plot
        x = numpy.array(x)
        y = numpy.array(y)
        plot = holoviews.Curve(
            data=pandas.DataFrame({"x": x, "y": 100*y}),
            kdims=[("x", "Year of inclusion")],
            vdims=[("y", "Indicator value (%)")]
        ).opts(
            xlabel=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
            ylabel="Indicator value",
            yformatter='%d%%',
            title="Indicator value by year of inclusion",
            show_grid=True,
            tools=["hover"],
            color="blue"
        )
        return plot

def get_dataframe_for_tabulator__binding_callback(df_clean, sex_selector_widget, age_range_selector_widget, age_range_min_max):
    # get the indices to build the sub-table
    years = [int(y) for y in list(set(df_clean["ANNO_DI_INCLUSIONE"]))]
    years.sort()
    denominator_filter = numpy.zeros(len(df_clean), dtype=bool)
    for year in years:
        _, d = get_clean_dataframe_filters_for_numerator_and_denominator(df_clean, year, sex_selector_widget, age_range_selector_widget, age_range_min_max)
        denominator_filter = denominator_filter | d
    if sex_selector_widget == "Unk.":
        # in the table, I want to show just the unknowns, so I have to consider them in the denominator
        denominator_filter = denominator_filter & (df_clean["SESSO"] == "Unk.")
    # get subtable and return it
    dataframe_to_display_into_tabulator = df_clean.loc[denominator_filter, :]
    return dataframe_to_display_into_tabulator

def get_box_element(df_global, disease, cohort, indicator):
    """ The box element is a row, containing a column with title, description of the indicator,
        a row with a plot and a table side by side, and widgets to interact with the plot and the table.
    """
    df = clean_global_dataframe_by_disease_cohort_indicator(df_global, disease, cohort, indicator)
    # - title
    title_panel = panel.panel(
        "<h1>" + indicator + "</h1>",
        styles={"text-align": "left"}
    )
    # - description
    description_panel = panel.panel(
        "<p>(Optional) description of the indicator</p>",
        styles={"text-align": "left", "color": "#546e7a", "font-size": "0.7em"}
    )
    # widgets - sex selector
    sex_selector_widget = panel.widgets.Select(
        name=database_keys_map[display_language]["SESSO"],
        value="All",
        options=["M", "F", "M and F", "Unk.", "All"]
    )
    # widgets - age selector
    age_min = max(18, min([int(y) for y in df["AGE"] if y != "Unk."]))
    age_max = max(90, max([int(y) for y in df["AGE"] if y != "Unk."]))
    age_range_selector_widget = panel.widgets.RangeSlider(
        name='Age range', 
        start=age_min, 
        end=age_max,
        value=(20, 30),
        step=1,
        format=bokeh.models.formatters.PrintfTickFormatter(format='%d y.o.')
    )
    widget_row = panel.WidgetBox(
        sex_selector_widget,
        age_range_selector_widget
    )
    # - plot
    plot_pane = panel.bind(
        get_plot__binding_callback,
        df_clean=df,
        sex_selector_widget=sex_selector_widget,
        age_range_selector_widget=age_range_selector_widget,
        age_range_min_max=(age_min, age_max)
    )
    # table
    table_widget = panel.widgets.Tabulator(
        panel.bind(
            get_dataframe_for_tabulator__binding_callback,
            df_clean=df,
            sex_selector_widget=sex_selector_widget,
            age_range_selector_widget=age_range_selector_widget,
            age_range_min_max=(age_min, age_max)
        ),
        theme='modern',
        pagination='remote', 
        page_size=10
    )
    ###############                                                       MAKE BINDING ALSO FOR TABLE SEX AND AGE
    
    # box element
    box_element = panel.Column(
        title_panel,
        description_panel,
        panel.Row(
            panel.Column(
                plot_pane,
                widget_row
            ),
            table_widget
        ),
        sizing_mode='stretch_width',
        styles={
            "margin-top": "0.5em",
            "margin-bottom": "0.5em"
        }
    )
    return box_element









##################
# Dashboard
##################

# - TITLE AND DISEASE SELECTOR

if not DB is None:
    disturbi = list(set(DB["DISTURBO"]))
    disturbi.sort()
    disturbi = numpy.insert(disturbi, 0, "ALL")
    title_choice_map = {diseases_map[display_language][k]: diseases_map[display_language][k] for k in disturbi}

title_menu_items = [(k, v) for k, v in title_choice_map.items()]

disease_word_langauges_map = {
    "en": "Disease",
    "it": "Disturbo",
    "fr": "Trouble",
    "de": "Störung",
    "es": "Trastorno",
    "pt": "Distúrbio"
}

title_menu_button_name_map = {
    "en": "Select disease",
    "it": "Seleziona disturbo",
    "fr": "Sélectionnez le trouble",
    "de": "Wählen Sie die Störung",
    "es": "Seleccione el trastorno",
    "pt": "Selecione o distúrbio"
}
title_menu_button = panel.widgets.MenuButton(
    name=title_menu_button_name_map[display_language],
    items=title_menu_items,
    button_type='warning',
    max_width=300,
    min_width=150,
    styles={
        "margin-right": "2em"
    } 
)

title_menu_button.param.set_param(clicked=title_menu_items[0][0])

default_title_message_map = {
    "en": "Select a disease from the dropdown menu on the right.",
    "it": "Seleziona un disturbo dal menu a tendina a destra.",
    "fr": "Sélectionnez un trouble dans le menu déroulant à droite.",
    "de": "Wählen Sie eine Störung aus dem Dropdown-Menü rechts aus.",
    "es": "Seleccione un trastorno del menú desplegable a la derecha.",
    "pt": "Selecione um distúrbio no menu suspenso à direita."
}
all_diseases_title_message_map = {
    "en": "Overview on all diseases",
    "it": "Panoramica di tutti i disturbi",
    "fr": "Aperçu de tous les troubles",
    "de": "Übersicht über alle Störungen",
    "es": "Descripción general de todos los trastornos",
    "pt": "Visão geral de todos os distúrbios"
}
def disease_selector_row_title_maker(value):
    if value is None:
        value = """<span style="font-size: 1.1em; color: #888888ff;">
                """+default_title_message_map[display_language]+"""
                </span>"""
    if value == diseases_map[display_language]["ALL"]:
        value = all_diseases_title_message_map[display_language]
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

coorte_language_map = {
    "en": {n: "Cohort "+n for n in ["A", "B", "C", "D"]},
    "it": {n: "Coorte "+n for n in ["A", "B", "C", "D"]},
    "fr": {n: "Cohorte "+n for n in ["A", "B", "C", "D"]},
    "de": {n: "Kohorte "+n for n in ["A", "B", "C", "D"]},
    "es": {n: "Cohorte "+n for n in ["A", "B", "C", "D"]},
    "pt": {n: "Cohorte "+n for n in ["A", "B", "C", "D"]}
}

coorte_explain_dict = {
    "en": {
        "Cohort A": "The \"prevalent cohort\" treated is made up of all beneficiaries of the National Health Service (NHS) resident in a given region who, in the year of inclusion, have had a suggestive contact of bipolar disorder with a structure accredited by the NHS.",
        "Cohort B": "The \"new patients taken in charge cohort\" (or incidents) is made up of the portion of the prevalent cohort that, in the two years preceding the year of inclusion, has not experienced any suggestive contact of bipolar disorder with a structure accredited by the NHS.",
        "Cohort C": "The \"new cases taken in charge cohort with onset disorder\" is made up of the portion of the new cases taken in charge cohort that, in the year of inclusion, has an age less than or equal to 25 years.",
        "Cohort D": "The \"discharged patients cohort from hospitalization in Psychiatric Diagnosis and Care Service\" (SPDC) is made up of the portion of the prevalent treated cohort that in the year of inclusion has experienced at least one hospitalization in a SPDC Service or other psychiatric structures for acute events."
    },
    "it": {
        "Coorte A": "La \"coorte prevalente\" trattata è costituita da tutti i beneficiari del Servizio Sanitario Nazionale (SSN) residenti in una data regione che, nell'anno di inclusione, hanno avuto un contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
        "Coorte B": "La \"coorte dei nuovi pazienti presi in carico\" (o incidenti) è costituita dalla porzione della coorte prevalente che, nei due anni precedenti l'anno di inclusione, non ha sperimentato alcun contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
        "Coorte C": "La \"coorte dei nuovi casi presi in carico con disturbo all'esordio\" è costituita dalla porzione della coorte dei nuovi casi presi in carico che, nell'anno di inclusione, ha un'età inferiore o uguale ai 25 anni compiuti.",
        "Coorte D": "La \"coorte dei pazienti dimessi da ricovero in Servizio Psichiatrico di Diagnosi e Cura\" (SPDC) è costituita dalla porzione della coorte prevalente trattata che nell'anno di inclusione ha sperimentato almeno un ricovero in un Servizio SPDC o altre strutture psichiatriche per eventi acuti."
    },
    "fr": {
        "Cohort A": "La \"cohorte prévalente\" traitée est constituée de tous les bénéficiaires du Service national de santé (SNS) résidant dans une région donnée qui, au cours de l'année d'inclusion, ont eu un contact suggestif de trouble bipolaire avec une structure agréée par le SNS.",
        "Cohort B": "La \"cohorte des nouveaux patients pris en charge\" (ou incidents) est constituée de la partie de la cohorte prévalente qui, au cours des deux années précédant l'année d'inclusion, n'a eu aucun contact suggestif de trouble bipolaire avec une structure agréée par le SNS.",
        "Cohort C": "La \"cohorte des nouveaux cas pris en charge avec trouble débutant\" est constituée de la partie de la cohorte des nouveaux cas pris en charge qui, au cours de l'année d'inclusion, a un âge inférieur ou égal à 25 ans.",
        "Cohort D": "La \"cohorte des patients sortis d'hospitalisation en service de diagnostic et de soins psychiatriques\" (SPDC) est constituée de la partie de la cohorte prévalente traitée qui, au cours de l'année d'inclusion, a connu au moins une hospitalisation dans un service SPDC ou d'autres structures psychiatriques pour des événements aigus."
    },
    "de": {
        "Kohorte A": "Die behandelte \"prävalente Kohorte\" besteht aus allen Leistungsempfängern des Nationalen Gesundheitsdienstes (NHS), die in einer bestimmten Region ansässig sind und im Jahr der Aufnahme einen suggestiven Kontakt mit einer vom NHS akkreditierten Einrichtung hatten.",
        "Kohorte B": "Die \"neu aufgenommene Patientenkohorte\" (oder Vorfälle) besteht aus dem Teil der prävalenten Kohorte, der in den zwei Jahren vor dem Aufnahmejahr keinen suggestiven Kontakt mit einer vom NHS akkreditierten Einrichtung hatte.",
        "Kohorte C": "Die \"neue Fallkohorte mit Beginn der Störung\" besteht aus dem Teil der neuen Fallkohorte, der im Aufnahmejahr ein Alter von weniger als oder gleich 25 Jahren aufweist.",
        "Kohorte D": "Die \"entlassene Patientenkohorte aus der Hospitalisierung im Psychiatrie-Diagnose- und Behandlungsdienst\" (SPDC) besteht aus dem Teil der behandelten prävalenten Kohorte, der im Aufnahmejahr mindestens einen Krankenhausaufenthalt in einem SPDC-Dienst oder anderen psychiatrischen Einrichtungen für akute Ereignisse hatte."
    },
    "es": {
        "Cohorte A": "La \"cohorte prevalente\" tratada está formada por todos los beneficiarios del Servicio Nacional de Salud (SNS) residentes en una determinada región que, en el año de inclusión, han tenido un contacto sugestivo de trastorno bipolar con una estructura acreditada por el SNS.",
        "Cohorte B": "La \"cohorte de nuevos pacientes atendidos\" (o incidentes) está formada por la parte de la cohorte prevalente que, en los dos años anteriores al año de inclusión, no ha tenido ningún contacto sugestivo de trastorno bipolar con una estructura acreditada por el SNS.",
        "Cohorte C": "La \"cohorte de nuevos casos atendidos con trastorno de inicio\" está formada por la parte de la cohorte de nuevos casos atendidos que, en el año de inclusión, tiene una edad inferior o igual a 25 años.",
        "Cohorte D": "La \"cohorte de pacientes dados de alta de la hospitalización en el servicio de diagnóstico y tratamiento psiquiátrico\" (SPDC) está formada por la parte de la cohorte prevalente tratada que en el año de inclusión ha experimentado al menos una hospitalización en un servicio SPDC u otras estructuras psiquiátricas para eventos agudos."
    },
    "pt": {
        "Cohorte A": "A \"coorte prevalente\" tratada é composta por todos os beneficiários do Serviço Nacional de Saúde (SNS) residentes numa determinada região que, no ano de inclusão, tiveram um contacto sugestivo de perturbação bipolar com uma estrutura acreditada pelo SNS.",
        "Cohorte B": "A \"coorte de novos pacientes atendidos\" (ou incidentes) é composta pela parte da coorte prevalente que, nos dois anos anteriores ao ano de inclusão, não teve qualquer contacto sugestivo de perturbação bipolar com uma estrutura acreditada pelo SNS.",
        "Cohorte C": "A \"coorte de novos casos atendidos com distúrbio de início\" é composta pela parte da coorte de novos casos atendidos que, no ano de inclusão, tem uma idade inferior ou igual a 25 anos.",
        "Cohorte D": "A \"coorte de pacientes dados de alta da hospitalização no serviço de diagnóstico e tratamento psiquiátrico\" (SPDC) é composta pela parte da coorte prevalente tratada que no ano de inclusão experimentou pelo menos uma hospitalização num serviço SPDC ou outras estruturas psiquiátricas para eventos agudos."
    }
}

coorte_button_options_list = [
    v for v in coorte_explain_dict[display_language].keys()
]

coorte_radio_group = panel.widgets.RadioButtonGroup(
    name='coorte selector', 
    options=coorte_button_options_list, 
    value=coorte_button_options_list[0],
    button_type='primary'
)

def build_coorte_tooltip_html(value: str, text: str):
    s_ = """
        <p style="
            color: #888888ff;
            font-size: 0.9em;
            text-align: center;
        ">
    """
    s_ += "<span style='color:#707070ff;'><b>"+value+"</b></span></br>"
    e_ = "</p>"
    text = text.replace("\"", """<span style='color:#707070ff;'><b>""", 1)
    text = text.replace("\"", """</b></span>""", 1)
    return s_ + text + e_

def update_coorte_html(value):
    return panel.pane.HTML(build_coorte_tooltip_html(value, coorte_explain_dict[display_language][value]))

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










# - MAIN BODY - PLOTS AND TABLES

def get_main_box_elements(df, disease_selector_value, coorte_selector_value):
    if disease_selector_value == diseases_map[display_language]["ALL"]:
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion, DB, coorte_radio_group.param.value)
        ]
    else:
        # clean input
        disease_selector_value = dict_find_key_by_value(diseases_map[display_language], disease_selector_value)
        coorte_selector_value = str(coorte_selector_value)[-1].upper()
        # find list of all indicators available for that disease and cohort
        list_of_boxes_to_display = []
        selection = (df["DISTURBO"] == disease_selector_value)
        selection = selection & (df["COORTE"] == coorte_selector_value)
        indicators = list(set(df.loc[selection,"INDICATORE"]))
        indicators.sort()
        # get all plots and elements
        for indicator in indicators:
            list_of_boxes_to_display.append(
                get_box_element(df, disease_selector_value, coorte_selector_value, indicator)
            )
        return list_of_boxes_to_display
    

main_box = panel.Column(
    objects=panel.bind(
        get_main_box_elements,
        df=DB,
        disease_selector_value=title_menu_button.param.clicked, 
        coorte_selector_value=coorte_radio_group.param.value
    ),
    align="center",
    styles={
        "width": "95%"
    }
)


# - BODY

body = panel.Column(
    top_selector_row,
    main_box,
    panel.Spacer(height=50),
    styles={
        "margin-top": "20px",
        "padding-top": "0px",
        "margin-bottom": "35px"
    }
)












##################
# Dashboard
##################

APP = panel.Column(
    header,
    body,
    footer,
    styles={
        "background": "#ffffffff",
        "width": 'calc(100vw - 17px)',
        "height": "100%"
    }
)
APP.show()