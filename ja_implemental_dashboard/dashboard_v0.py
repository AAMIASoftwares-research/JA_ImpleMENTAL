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


#####################
# LANGUAGE SELECTION 
#####################

AVAILABLE_LANGUAGES = ["en", "it", "fr", "de", "es", "pt"]
display_language = AVAILABLE_LANGUAGES[0]

##############
# DIRECTORIES
##############

DATA_FOLDER = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/"
)




########
# header
########

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


########
# footer
########

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
    "TOT_INTERVENTI": numpy.random.poisson(2, n_rows) # indicatore si calcola con questo
})
# Dove anno nascita is None, anche mese nascita deve essere none
df.loc[df["MESE_NASCITA"].isnull(), "ANNO_NASCITA"] = None
df.loc[df["ANNO_NASCITA"].isnull(), "MESE_NASCITA"] = None
# Cambia TOT_INTERVENTI in base a indicatore, così da avere grafici un po diversi
df.loc[df["INDICATORE"] == "Indicatore 1", "TOT_INTERVENTI"] = (df.loc[df["INDICATORE"] == "Indicatore 1", "TOT_INTERVENTI"] - 1).clip(lower=0)
df.loc[df["INDICATORE"] == "Indicatore 2", "TOT_INTERVENTI"] = (df.loc[df["INDICATORE"] == "Indicatore 2", "TOT_INTERVENTI"] - 2).clip(lower=0)
# Dove TOT_INTERVENTI is 0, qualche volta lo mettiamo come None o NaN, così il codice a valle risulta piu robusto
df.loc[df["TOT_INTERVENTI"] == 0, "TOT_INTERVENTI"] = numpy.random.choice(
    [0, None, None, None, numpy.nan, numpy.nan], len(df.loc[df["TOT_INTERVENTI"] == 0, "TOT_INTERVENTI"]),
    replace=True
)



################
# All diseases page
################

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
    pl = df3.hvplot.bar(
        x=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
        y=[diseases_map[display_language][d] for d in disturbi[1:]],
        stacked=True,
        xlabel=database_keys_map[display_language]["ANNO_DI_INCLUSIONE"],
        ylabel=y_abels_map[display_language],
        title=plot_title_map[display_language],
        legend="top_left",
        max_width=600
    )
    if 0:
        hvplot.show(pl)
    else:
        return pl

def plot_all_diseases_by_year_of_inclusion_binding_coorte(coorte="Coorte A"):
    return plot_all_diseases_by_year_of_inclusion(df, coorte=coorte)


##################
# Single disease page
##################

# - depending on the selected disease, cohort, and indicator, plot
# the history (by year of inclusion on the x axis) of the number of patients
# Also stratify the patients by sex and age (in 5 years intervals)


def plot_indicatore_time_series_plus_stratification(
        df_global,
        disease,
        cohort,
        indicator
        ):
    """
    stratification: m-f, age
    x: year of inclusion
    y: indicatore (number of interventions != 0 / number of patients)
    """
    # select data to plot and put it into a different dataframe
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
    # add age group column ordered by 18-25, 26-35, 36-45, 46-55, 56-65, over 65  
    AGE_GROUPS = ["18-25", "26-35", "36-45", "46-55", "56-65", "over 65", "Unknown age", "any age"]
    df["AGE_GROUP"] = df["AGE"]
    df.loc[df["AGE"] <= 25, "AGE_GROUP"] = "18-25"
    df.loc[(df["AGE"] > 25) & (df["AGE"] <= 35), "AGE_GROUP"] = "26-35"
    df.loc[(df["AGE"] > 35) & (df["AGE"] <= 45), "AGE_GROUP"] = "36-45"
    df.loc[(df["AGE"] > 45) & (df["AGE"] <= 55), "AGE_GROUP"] = "46-55"
    df.loc[(df["AGE"] > 55) & (df["AGE"] <= 65), "AGE_GROUP"] = "56-65"
    df.loc[df["AGE"] > 65, "AGE_GROUP"] = "over 65"
    df.loc[df["AGE"].isna(), "AGE_GROUP"] = "Unknown age"
    # clean TOT_INTERVENTI from NaN
    df.loc[df["TOT_INTERVENTI"].isna(), "TOT_INTERVENTI"] = 0
    # clean SESSO from NaN and None and subtitute with "Unknown"
    BIOLOGICAL_BIRTH_SEXES = ["M", "F", "Unknown sex", "any sex"]
    df.loc[df["SESSO"].isna(), "SESSO"] = "Unknown sex"
    # - anno di inclusione
    anno_di_inclusione = list(set(df["ANNO_DI_INCLUSIONE"]))
    anno_di_inclusione.sort()
    
    #######      old pipeline      #######
    ######################################
    ######################################
    plot_lists_year_of_inclusion = []
    plot_lists_age_group = []
    plot_list_sex = []
    plot_list_indicator_value = []
    for anno in anno_di_inclusione:
        for age_group in AGE_GROUPS:
            for sex in BIOLOGICAL_BIRTH_SEXES:
                plot_lists_year_of_inclusion.append(anno)
                plot_lists_age_group.append(age_group)
                plot_list_sex.append(sex)
                # stratify
                df_temp_ = df.loc[df["ANNO_DI_INCLUSIONE"] == anno, :]
                num_patients_in_reference_year = len(df_temp_)
                if age_group == "any age":
                    pass
                else:
                    df_temp_ = df_temp_.loc[df_temp_["AGE_GROUP"] == age_group, :]
                if sex == "any sex":
                    pass
                else:
                    df_temp_ = df_temp_.loc[df_temp_["SESSO"] == sex, :]
                # make indicator value
                num_patients_with_interventions = len(df_temp_.loc[df_temp_["TOT_INTERVENTI"] != 0, :])
                indicator_value = num_patients_with_interventions / num_patients_in_reference_year
                #####################
                ##################### stratificando, devo stratificare anche il denominatore o
                ##################### soltanto il numeratore? Io direi anche il denominatore
                ##################### (es. maschi con almeno un intervento / maschi totali)
                ##################### ma prima meglio chiedere
                #####################  CHIEDERE AI CAPI ------------------------------------------
                plot_list_indicator_value.append(indicator_value)
    # build dataframe
    df_plot = pandas.DataFrame({
        "YEAR_OF_INCLUSION": plot_lists_year_of_inclusion,
        "AGE_GROUP": plot_lists_age_group,
        "SEX": plot_list_sex,
        "INDICATOR_VALUE": plot_list_indicator_value
    })


    #######      new pipeline      #######
    ######## intractive dataframe ########
    ######################################
    # a working example: https://gist.github.com/MarcSkovMadsen/ffb273636dced88705c8c88d5ee28f23

    # - slider widget for age grouping
    range_slider = panel.widgets.EditableRangeSlider(
        # https://holoviz.org/tutorial/Interactive_Pipelines.html
        name='Scegli età', 
        start=18, end=90,
        value=(20, 30),
        step=1,
        format=bokeh.models.formatters.PrintfTickFormatter(format='%d anni')
    )
    print("\n\n\n")
    # - dropdown widget for sex grouping 

    # - interactive datarame
    dfi = df.interactive()
    filtered_df = dfi[(dfi['AGE'] >= range_slider.value[0]) & (dfi['AGE'] <= range_slider.value[1])].head(10)
    
    pipeline = (
        df.interactive()[(df['AGE'] >= range_slider.value[0]) & (df['AGE'] <= range_slider.value[1])]
    )
    

    # - example of interactive plotn - a table
    # https://panel.holoviz.org/reference/panes/Table.html
    # Interactive Table
    table = pipeline.pipe(
        panel.widgets.Tabulator,
        pagination="remote",
        page_size=20,
        theme="fast",
        sizing_mode="stretch_both",
    ).panel(name="Table")

    # - plot it for debugging
    p = panel.Column(
        table,
        range_slider
    )
    p.show()
    quit()
    

    





    ## from https://holoviews.org/reference/elements/bokeh/Bars.html
    # and https://justinbois.github.io/bootcamp/2022/lessons/l40_holoviews.html
    age_group_dimension_picker = holoviews.Dimension('AGE_GROUP', values=['any age'])
    sex_dimension_picker = holoviews.Dimension("SEX", values=["Unknown sex", "M", "F"])
    bars = holoviews.Bars(
        df_plot,
        kdims=["YEAR_OF_INCLUSION", sex_dimension_picker, 'AGE_GROUP'],
        vdims=["INDICATOR_VALUE"],
        ylabel=indicator,
        title="Indicator value by year of inclusion" ### translate
        
    ).groupby(
        ['AGE_GROUP']
    ).opts(
        stacked=True, tools=['hover'], width=800
    )
    
    ###    also make table to the right (plot + table, you have to use the + operator)
    if 1:
        hvplot.show(bars)
    else:
        return bars


def plot_indicatore_time_series_stratification_and_table_idf(df_global,
        disease,
        cohort,
        indicator
        ):
    """
    stratification: m-f, age
    x: year of inclusion
    y: indicatore (number of interventions != 0 / number of patients)
    """
    # kind of as the previous function, but with a table
    # also, i'm using interactive dataframe from holoviz to try and simplify everything



plot_indicatore_time_series_plus_stratification(df, "BIPO", "A", "Indicatore 1")
quit()




##################
# Dashboard
##################

# - TITLE AND DISEASE SELECTOR

if not df is None:
    disturbi = list(set(df["DISTURBO"]))
    disturbi.sort()
    disturbi = numpy.insert(disturbi, 0, "ALL")
    title_choice_map = {diseases_map[display_language][k]: diseases_map[display_language][k] for k in disturbi}

title_menu_items = [(k, v) for k, v in title_choice_map.items()]

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
    return panel.pane.HTML(build_coorte_tooltip_html(coorte_explain_dict[display_language][value]))

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
    if disease_selector_value == diseases_map[display_language]["ALL"]:
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion_binding_coorte, coorte_radio_group.param.value)
        ]
    ###### put here the rest of the logic
    else:
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion_binding_coorte, coorte_radio_group.param.value),
            plot_all_diseases_by_year_of_inclusion(df),
            plot_all_diseases_by_year_of_inclusion(df),
            #plot_all_diseases_by_year_of_inclusion(df),
            #plot_all_diseases_by_year_of_inclusion(df)
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