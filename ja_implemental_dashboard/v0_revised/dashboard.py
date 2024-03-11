# Author: Matteo Leccardi
# Interesting resources:
# https://holoviz.org/tutorial/index.html
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
    #design='material',
    sizing_mode='stretch_width'
)

from ..sas_database_reader import read_sas_database_ind_1

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

choice_disturbo = ["BIPO", "SCHIZO", "DISEASE1", "DISEASE2"]
choice_coorte = ["A", "B", "C", "D"]
choice_anno_di_inclusione = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
choice_indictore = ["Indicatore 1", "Indicatore 2", "Indicatore 3"]
choice_sex = ["M", "F"]*50 + [None]
choice_anno_nascita = [i for i in range(1948, 2011)] + [None]
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

















########################
# LANGUAGE DICTIONARIES
########################

# All dictionaries are gathered here, ordered by section of the dashboard

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
AVAILABLE_LANGUAGES = [v for v in LANGUAGE_DICT.values()]
DEFAULT_LANGUAGE = "en"

# - HEADER

eu_funding_string_langmap = {
    "en": "Co-funded by the European Union",
    "it": "Co-finanziato dall'Unione Europea",
    "fr": "Co-financé par l'Union européenne",
    "de": "Mitfinanziert von der Europäischen Union",
    "es": "Cofinanciado por la Unión Europea",
    "pt": "Co-financiado pela União Europeia"
}  ### the one displayed is just an image, so this is not used yet  -> make image of just the flag


title_str_html_langmap = {
    "en": "Joint Action on Implementation of Best Practices </br> in the area of Mental Health",
    "it": "\"Joint Action\" sull'implementazione delle migliori pratiche </br> nel campo della salute mentale",
    "fr": "\"Joint Action\" sur la mise en œuvre des meilleures pratiques </br> dans le domaine de la santé mentale",
    "de": "\"Joint Action\" zur Umsetzung bewährter Verfahren im Bereich </br> der psychischen Gesundheit",
    "es": "\"Joint Action\" sobre la implementación de las mejores prácticas </br> en el ámbito de la salud mental",
    "pt": "\"Joint Action\" sobre a implementação das melhores práticas </br> no domínio da saúde mental",
}

language_selector_title_langmap = {
    "en": 'Language',
    "it": "Lingua",
    "fr": "Langue",
    "de": "Sprache",
    "es": "Idioma",
    "pt": "Língua"
}

home_button_str_html_langmap = {
    "en": "Project homepage",
    "it": "Homepage del progetto",
    "fr": "Page d'accueil du projet",
    "de": "Projekt-Homepage",
    "es": "Página de inicio del proyecto",
    "pt": "Página inicial do projeto"
}

dashboard_button_str_html_langmap = {
    "en": "Go to dashboard",
    "it": "Vai alla dashboard",
    "fr": "Aller au dashboard",
    "de": "Zur Übersicht gehen",
    "es": "Ir al dashboard",
    "pt": "Ir para o dashboard"
}

# - FOOTER

footer_str_html_langmap = {
    "en": """JA ImpleMENTAL is a Joint Action (JA) co-funded by the European Commission (EC)
                under the Third Health Programme (2014-2020). 
                The JA ImpleMENTAL project aims to improve the quality of mental health care in
                Europe by identifying, analysing and exchanging good practices in mental health care.""",
    "it": """JA ImpleMENTAL è un'azione congiunta (JA) cofinanziata dalla Commissione europea (CE)
                nell'ambito del terzo programma sanitario (2014-2020). 
                Il progetto JA ImpleMENTAL mira a migliorare la qualità dell'assistenza sanitaria
                mentale in Europa identificando, analizzando e scambiando buone pratiche nell'assistenza
                sanitaria mentale.""",
    "fr": """JA ImpleMENTAL est une action conjointe (JA) cofinancée par la Commission européenne (CE)
                dans le cadre du troisième programme de santé (2014-2020). 
                Le projet JA ImpleMENTAL vise à améliorer la qualité des soins de santé mentale en Europe
                en identifiant, analysant et échangeant les bonnes pratiques en matière de soins de santé
                mentale.""",
    "de": """JA ImpleMENTAL ist eine Joint Action (JA), die von der Europäischen Kommission (EK)
                im Rahmen des Dritten Gesundheitsprogramms (2014-2020) kofinanziert wird. 
                Das Projekt JA ImpleMENTAL zielt darauf ab, die Qualität der psychischen Gesundheitsversorgung in Europa
                durch die Identifizierung, Analyse und den Austausch bewährter Praktiken 
                in der psychischen Gesundheitsversorgung zu verbessern.""",
    "es": """JA ImpleMENTAL es una Acción Conjunta (JA) cofinanciada por la Comisión Europea (CE)
                en el marco del Tercer Programa de Salud (2014-2020). 
                El proyecto JA ImpleMENTAL tiene como objetivo mejorar la calidad de la atención de salud mental en Europa
                mediante la identificación, el análisis y el intercambio de buenas prácticas en la atención de salud mental.""",
    "pt": """JA ImpleMENTAL é uma Ação Conjunta (JA) cofinanciada pela Comissão Europeia (CE)
                no âmbito do Terceiro Programa de Saúde (2014-2020). 
                O projeto JA ImpleMENTAL tem como objetivo melhorar a qualidade do atendimento de saúde mental na Europa
                identificando, analisando e trocando boas práticas no atendimento de saúde mental."""
}

# - TITLE AND DISEASE SELECTOR

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

default_title_message_langmap = {
    "en": "Select a disease from the dropdown menu on the right.",
    "it": "Seleziona un disturbo dal menu a tendina a destra.",
    "fr": "Sélectionnez un trouble dans le menu déroulant à droite.",
    "de": "Wählen Sie eine Störung aus dem Dropdown-Menü rechts aus.",
    "es": "Seleccione un trastorno del menú desplegable a la derecha.",
    "pt": "Selecione um distúrbio no menu suspenso à direita."
}
all_diseases_title_message_langmap = {
    "en": "Overview on all diseases",
    "it": "Panoramica di tutti i disturbi",
    "fr": "Aperçu de tous les troubles",
    "de": "Übersicht über alle Störungen",
    "es": "Descripción general de todos los trastornos",
    "pt": "Visão geral de todos os distúrbios"
}

# - COORTE CHOICE

coorte_language_map = {
    "en": {n: "Cohort "+n for n in ["A", "B", "C"]}, # ["A", "B", "C", "D"] -> D got discarded
    "it": {n: "Coorte "+n for n in ["A", "B", "C"]},
    "fr": {n: "Cohorte "+n for n in ["A", "B", "C"]},
    "de": {n: "Kohorte "+n for n in ["A", "B", "C"]},
    "es": {n: "Cohorte "+n for n in ["A", "B", "C"]},
    "pt": {n: "Cohorte "+n for n in ["A", "B", "C"]}
}

coorte_explain_dict = {
    "en": {
        "Cohort A": "The \"prevalent cohort\" treated is made up of all beneficiaries of the National Health Service (NHS) resident in a given region who, in the year of inclusion, have had a suggestive contact of bipolar disorder with a structure accredited by the NHS.",
        "Cohort B": "The \"new patients taken in charge cohort\" (or incidents) is made up of the portion of the prevalent cohort that, in the two years preceding the year of inclusion, has not experienced any suggestive contact of bipolar disorder with a structure accredited by the NHS.",
        "Cohort C": "The \"new cases taken in charge cohort with onset disorder\" is made up of the portion of the new cases taken in charge cohort that, in the year of inclusion, has an age less than or equal to 25 years.",
        #"Cohort D": "The \"discharged patients cohort from hospitalization in Psychiatric Diagnosis and Care Service\" (SPDC) is made up of the portion of the prevalent treated cohort that in the year of inclusion has experienced at least one hospitalization in a SPDC Service or other psychiatric structures for acute events."
    },
    "it": {
        "Coorte A": "La \"coorte prevalente\" trattata è costituita da tutti i beneficiari del Servizio Sanitario Nazionale (SSN) residenti in una data regione che, nell'anno di inclusione, hanno avuto un contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
        "Coorte B": "La \"coorte dei nuovi pazienti presi in carico\" (o incidenti) è costituita dalla porzione della coorte prevalente che, nei due anni precedenti l'anno di inclusione, non ha sperimentato alcun contatto suggestivo di disturbo bipolare con una struttura accreditata dal SSN.",
        "Coorte C": "La \"coorte dei nuovi casi presi in carico con disturbo all'esordio\" è costituita dalla porzione della coorte dei nuovi casi presi in carico che, nell'anno di inclusione, ha un'età inferiore o uguale ai 25 anni compiuti.",
        #"Coorte D": "La \"coorte dei pazienti dimessi da ricovero in Servizio Psichiatrico di Diagnosi e Cura\" (SPDC) è costituita dalla porzione della coorte prevalente trattata che nell'anno di inclusione ha sperimentato almeno un ricovero in un Servizio SPDC o altre strutture psichiatriche per eventi acuti."
    },
    "fr": {
        "Cohort A": "La \"cohorte prévalente\" traitée est constituée de tous les bénéficiaires du Service national de santé (SNS) résidant dans une région donnée qui, au cours de l'année d'inclusion, ont eu un contact suggestif de trouble bipolaire avec une structure agréée par le SNS.",
        "Cohort B": "La \"cohorte des nouveaux patients pris en charge\" (ou incidents) est constituée de la partie de la cohorte prévalente qui, au cours des deux années précédant l'année d'inclusion, n'a eu aucun contact suggestif de trouble bipolaire avec une structure agréée par le SNS.",
        "Cohort C": "La \"cohorte des nouveaux cas pris en charge avec trouble débutant\" est constituée de la partie de la cohorte des nouveaux cas pris en charge qui, au cours de l'année d'inclusion, a un âge inférieur ou égal à 25 ans.",
        #"Cohort D": "La \"cohorte des patients sortis d'hospitalisation en service de diagnostic et de soins psychiatriques\" (SPDC) est constituée de la partie de la cohorte prévalente traitée qui, au cours de l'année d'inclusion, a connu au moins une hospitalisation dans un service SPDC ou d'autres structures psychiatriques pour des événements aigus."
    },
    "de": {
        "Kohorte A": "Die behandelte \"prävalente Kohorte\" besteht aus allen Leistungsempfängern des Nationalen Gesundheitsdienstes (NHS), die in einer bestimmten Region ansässig sind und im Jahr der Aufnahme einen suggestiven Kontakt mit einer vom NHS akkreditierten Einrichtung hatten.",
        "Kohorte B": "Die \"neu aufgenommene Patientenkohorte\" (oder Vorfälle) besteht aus dem Teil der prävalenten Kohorte, der in den zwei Jahren vor dem Aufnahmejahr keinen suggestiven Kontakt mit einer vom NHS akkreditierten Einrichtung hatte.",
        "Kohorte C": "Die \"neue Fallkohorte mit Beginn der Störung\" besteht aus dem Teil der neuen Fallkohorte, der im Aufnahmejahr ein Alter von weniger als oder gleich 25 Jahren aufweist.",
        #"Kohorte D": "Die \"entlassene Patientenkohorte aus der Hospitalisierung im Psychiatrie-Diagnose- und Behandlungsdienst\" (SPDC) besteht aus dem Teil der behandelten prävalenten Kohorte, der im Aufnahmejahr mindestens einen Krankenhausaufenthalt in einem SPDC-Dienst oder anderen psychiatrischen Einrichtungen für akute Ereignisse hatte."
    },
    "es": {
        "Cohorte A": "La \"cohorte prevalente\" tratada está formada por todos los beneficiarios del Servicio Nacional de Salud (SNS) residentes en una determinada región que, en el año de inclusión, han tenido un contacto sugestivo de trastorno bipolar con una estructura acreditada por el SNS.",
        "Cohorte B": "La \"cohorte de nuevos pacientes atendidos\" (o incidentes) está formada por la parte de la cohorte prevalente que, en los dos años anteriores al año de inclusión, no ha tenido ningún contacto sugestivo de trastorno bipolar con una estructura acreditada por el SNS.",
        "Cohorte C": "La \"cohorte de nuevos casos atendidos con trastorno de inicio\" está formada por la parte de la cohorte de nuevos casos atendidos que, en el año de inclusión, tiene una edad inferior o igual a 25 años.",
        #"Cohorte D": "La \"cohorte de pacientes dados de alta de la hospitalización en el servicio de diagnóstico y tratamiento psiquiátrico\" (SPDC) está formada por la parte de la cohorte prevalente tratada que en el año de inclusión ha experimentado al menos una hospitalización en un servicio SPDC u otras estructuras psiquiátricas para eventos agudos."
    },
    "pt": {
        "Cohorte A": "A \"coorte prevalente\" tratada é composta por todos os beneficiários do Serviço Nacional de Saúde (SNS) residentes numa determinada região que, no ano de inclusão, tiveram um contacto sugestivo de perturbação bipolar com uma estrutura acreditada pelo SNS.",
        "Cohorte B": "A \"coorte de novos pacientes atendidos\" (ou incidentes) é composta pela parte da coorte prevalente que, nos dois anos anteriores ao ano de inclusão, não teve qualquer contacto sugestivo de perturbação bipolar com uma estrutura acreditada pelo SNS.",
        "Cohorte C": "A \"coorte de novos casos atendidos com distúrbio de início\" é composta pela parte da coorte de novos casos atendidos que, no ano de inclusão, tem uma idade inferior ou igual a 25 anos.",
        #"Cohorte D": "A \"coorte de pacientes dados de alta da hospitalização no serviço de diagnóstico e tratamento psiquiátrico\" (SPDC) é composta pela parte da coorte prevalente tratada que no ano de inclusão experimentou pelo menos uma hospitalização num serviço SPDC ou outras estruturas psiquiátricas para eventos agudos."
    }
}


# DATABASE ENTRIES

diseases_langmap = {
    "en": {
        "ALL": "All diseases",
        "BIPO": "Bipolar Disorder",
        "SCHIZO": "Schizophrenia",
        "DISEASE1": "Disease 1",
        "DISEASE2": "Disease 2"
    },
    "it": {
        "ALL": "Tutti i disturbi",
        "BIPO": "Disturbo bipolare",
        "SCHIZO": "Schizofrenia",
        "DISEASE1": "Disturbo 1",
        "DISEASE2": "Disturbo 2"
    },
    "fr": {
        "ALL": "Tous les troubles",
        "BIPO": "Trouble bipolaire",
        "SCHIZO": "Schizophrénie",
        "DISEASE1": "Trouble 1",
        "DISEASE2": "Trouble 2"
    },
    "de": {
        "ALL": "Alle Störungen",
        "BIPO": "Bipolare Störung",
        "SCHIZO": "Schizophrenie",
        "DISEASE1": "Störung 1",
        "DISEASE2": "Störung 2"
    },
    "es": {
        "ALL": "Todos los trastornos",
        "BIPO": "Trastorno bipolar",
        "SCHIZO": "Esquizofrenia",
        "DISEASE1": "Trastorno 1",
        "DISEASE2": "Trastorno 2"
    },
    "pt": {
        "ALL": "Todos os distúrbios",
        "BIPO": "Transtorno bipolar",
        "SCHIZO": "Esquizofrenia",
        "DISEASE1": "Transtorno 1",
        "DISEASE2": "Transtorno 2"
    }
}

database_keys_langmap = {
    "en": {
        "DISTURBO": "Disease",
        "COORTE": "Cohort",
        "ANNO_DI_INCLUSIONE": "Year of inclusion",
        "INDICATORE": "Indicator",
        "ID_ASSISTITO": "Patient ID",
        "SESSO": "Gender",
        "ANNO_NASCITA": "Year of birth",
        "MESE_NASCITA": "Month of birth",
        "MESI_FUP": "Months of follow up",
        "TOT_INTERVENTI": "Number of interventions",
        "AGE": "Age"
    },
    "it": {
        "DISTURBO": "Disturbo",
        "COORTE": "Coorte",
        "ANNO_DI_INCLUSIONE": "Anno di inclusione",
        "INDICATORE": "Indicatore",
        "ID_ASSISTITO": "ID Assistito",
        "SESSO": "Genere",
        "ANNO_NASCITA": "Anno di nascita",
        "MESE_NASCITA": "Mese di nascita",
        "MESI_FUP": "Mesi di follow up",
        "TOT_INTERVENTI": "Numero di interventi",
        "AGE": "Età"
    },
    "fr": {
        "DISTURBO": "Trouble",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Année d'inclusion",
        "INDICATORE": "Indicateur",
        "ID_ASSISTITO": "ID Patient",
        "SESSO": "Genre",
        "ANNO_NASCITA": "Année de naissance",
        "MESE_NASCITA": "Mois de naissance",
        "MESI_FUP": "Mois de suivi",
        "TOT_INTERVENTI": "Nombre d'interventions",
        "AGE": "Âge"
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
        "TOT_INTERVENTI": "Anzahl der Interventionen",
        "AGE": "Alter"
    },
    "es": {
        "DISTURBO": "Trastorno",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Año de inclusión",
        "INDICATORE": "Indicador",
        "ID_ASSISTITO": "ID del paciente",
        "SESSO": "Género",
        "ANNO_NASCITA": "Año de nacimiento",
        "MESE_NASCITA": "Mes de nacimiento",
        "MESI_FUP": "Meses de seguimiento",
        "TOT_INTERVENTI": "Número de intervenciones",
        "AGE": "Edad"
    },
    "pt": {
        "DISTURBO": "Distúrbio",
        "COORTE": "Cohorte",
        "ANNO_DI_INCLUSIONE": "Ano de inclusão",
        "INDICATORE": "Indicador",
        "ID_ASSISTITO": "ID do paciente",
        "SESSO": "Gênero",
        "ANNO_NASCITA": "Ano de nascimento",
        "MESE_NASCITA": "Mês de nascimento",
        "MESI_FUP": "Meses de acompanhamento",
        "TOT_INTERVENTI": "Número de intervenções",
        "AGE": "Idade"
    }
}

# INDICATORS PLOTS AND MAIN BOXES

indicator_langmap_it = {
    "en": {
        "Indicatore": "Indicator",
    },
    "it": {
        "Indicatore": "Indicatore",
    },
    "fr": {
        "Indicatore": "Indicateur",
    },
    "de": {
        "Indicatore": "Indikator",
    },
    "es": {
        "Indicatore": "Indicador",
    },
    "pt": {
        "Indicatore": "Indicador",
    }
}

sex_selector_langmap = {
        "en": {
            "M": "Males",
            "F": "Females",
            "M and F": "Males and Females",
            "Unk.": "Unknown",
            "All": "All"
        },
        "it": {
            "M": "Maschi",
            "F": "Femmine",
            "M and F": "Maschi e Femmine",
            "Unk.": "Sconosciuto",
            "All": "Tutti"
        },
        "fr": {
            "M": "Hommes",
            "F": "Femmes",
            "M and F": "Hommes et Femmes",
            "Unk.": "Inconnu",
            "All": "Tous"
        },
        "de": {
            "M": "Männer",
            "F": "Frauen",
            "M and F": "Männer und Frauen",
            "Unk.": "Unbekannt",
            "All": "Alle"
        },
        "es": {
            "M": "Hombres",
            "F": "Mujeres",
            "M and F": "Hombres y Mujeres",
            "Unk.": "Desconocido",
            "All": "Todos"
        },
        "pt": {
            "M": "Homens",
            "F": "Mulheres",
            "M and F": "Homens e Mulheres",
            "Unk.": "Desconhecido",
            "All": "Todos"
        }
    }

age_range_langmap = {
    "en": "Age range",
    "it": "Fascia d'età",
    "fr": "Tranche d'âge",
    "de": "Altersbereich",
    "es": "Rango de edad",
    "pt": "Faixa etária"
}

years_old_langmap = {
    "en": "y.o.",
    "it": "anni",
    "fr": "ans",
    "de": "J.a.",
    "es": "años",
    "pt": "anos"
}

indicator_value_langmap = {
    "en": "Indicator value",
    "it": "Valore dell'indicatore",
    "fr": "Valeur de l'indicateur",
    "de": "Indikatorwert",
    "es": "Valor del indicador",
    "pt": "Valor do indicador"
}

indicator_plot_title_langmap = {
    "en": "Indicator value by year of inclusion",
    "it": "Valore dell'indicatore per anno di inclusione",
    "fr": "Valeur de l'indicateur par année d'inclusion",
    "de": "Indikatorwert nach Jahr der Aufnahme",
    "es": "Valor del indicador por año de inclusión",
    "pt": "Valor do indicador por ano de inclusão"
}

proportions_text_plot_indicator_area_hover_langmap = {
    "en": {
        "M": "Males (% of numerator)",
        "F": "Females (% of numerator)"
    },
    "it": {
        "M": "Maschi (% del numeratore)",
        "F": "Femmine (% del numeratore)"
    },
    "fr": {
        "M": "Hommes (% du numérateur)",
        "F": "Femmes (% du numérateur)"
    },
    "de": {
        "M": "Männer (% des Zählers)",
        "F": "Frauen (% des Zählers)"
    },
    "es": {
        "M": "Hombres (% del numerador)",
        "F": "Mujeres (% del numerador)"
    },
    "pt": {
        "M": "Homens (% do numerador)",
        "F": "Mulheres (% do numerador)"
    }
}














#####################
# LANGUAGE SELECTION 
#####################


# make a dropdown menu and related binding callback
# so that language can be changed easily by the user

global display_language # This is the language used in the dashboard APP
                        # Global variables are not nice, but this is the easiest way without passing
                        # the language variable to every function.
display_language = DEFAULT_LANGUAGE 

# this is GLOBAL, so that it can be used in the callback
language_selector_widget = panel.widgets.Select(
    # no name, because we want to use a custom name
    value=DEFAULT_LANGUAGE,
    options=LANGUAGE_DICT,
    width=110,
    background="#00000020",
    styles={
        "border-radius": "3px",
        "margin-top": "0",
        "padding-top": "0",
    }
)

def language_selector_widget_make_name_html():
    global display_language
    text = language_selector_title_langmap[display_language]
    html = f"""<div style="
            text-align:center;
            margin-bottom: 1px;
            padding: 0px 0px 0px 0px;
            font-size: 0.9em;
            font-weight: 600;
            font-family: sans-serif;
            color: #333333;
        ">{text}</div>"""
    return panel.pane.HTML(html)

def get_header_language_selector():
    lsc = panel.Column(
        language_selector_widget_make_name_html,
        language_selector_widget,
        styles={
            "position": "absolute",
            "margin-top": "15px",
            "margin-left": "calc(100vw - 190px)",
            "background": "#ffffffb3",
            "border-radius": "5px"
        }
    )
    return lsc


# The callback and connection (binding) to change language to the whole app
# is at the bottom of this page of code, where the dashboard APP
# is defined.
# 
# To change the language of the whole app, it is necessary to have all the
# elements of the app in a single function, so that the callback can
# change the language of all the elements of the app.
# We divide this task in header's, body's, and footer's builder function,
# which could be themselves divided in smaller functions.
#
# Having everything declared into function is also useful to have a
# clean and readable code, and to have a single point of control
# for the whole app.
# This is also referred to as lambda architecture, and is a good practice
# for building dashboards and web apps.









#########
# HEADER
#########

def build_header():
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
            <div style="
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 100%;
                height: 100%;
            ">
                <h1 style="
                    margin-right: 1.5em;
                    font-style: normal;
                    font-weight: 600;
                    font-family: sans-serif;
                    font-size: 1.3em;
                    direction: ltr;
                    text-align: center;
                    color: #333333;
                    ">
                    """ + title_str_html_langmap[display_language] + """
                </h1>
                <div style="
                    display: flex;
                    flex-direction: row;
                    justify-content: center;
                    align-items: center;
                    width: 100%;
                    height: 100%;
                    margin-top: 1.2em;
                ">
                    <a href="https://ja-implemental.eu/" target="_blank" style="text-decoration: none;color: inherit;">
                        <button style="
                            margin-right: 1em;
                            color: #ffffff;
                            background-color: #3e7d98;
                            border: solid 3px #3e7d98;
                            border-radius: 500px;
                            padding: 0.5em 1em;
                            font-style: normal;
                            font-weight: 800;
                            font-family: sans-serif;
                            font-size: 1.4em;
                            direction: ltr;
                            text-align: center;
                            cursor: pointer;
                            transition: background-color .125s ease-in;
                        ">
                            """ + home_button_str_html_langmap[display_language] + """
                        </button>
                    </a>
                    <button onclick="window.scrollTo({ top: 312, behavior: 'smooth' })" style="
                        margin-left: 1em;
                        color: #3e7d98;
                        background-color: #ffffff;
                        border: solid 3px #ffffff;
                        border-radius: 500px;
                        padding: 0.5em 1em;
                        font-style: normal;
                        font-weight: 800;
                        font-family: sans-serif;
                        font-size: 1.4em;
                        direction: ltr;
                        text-align: center;
                        cursor: pointer;
                        transition: background-color .125s ease-in;
                    ">
                        """ + dashboard_button_str_html_langmap[display_language] + """
                    </button>
                </div>
            </div>
        </div>
        """,
        styles={
            "width": "calc(100vw - 17px)",
            "margin": "0",
            "padding": "0"
        }
    )
    # add the language selector widget to the header
    header = panel.Column(
        header,
        get_header_language_selector(),
        sizing_mode="stretch_width"
    )
    return header


#########
# FOOTER
#########

def build_footer():
    footer = panel.pane.HTML(
    """
    <footer style="
            z-index: 2147483646;
            position: absolute; 
            bottom: 0; 
            width: calc(100vw - 16px); 
            padding: 5px 0; 
            background-color: #e9ecef;
            border-radius: 16px 16px 0px 0px;
            border: solid 1px #555555;
            margin-bottom: -2px;
    ">
        <div style="
                display: flex; 
                align-items: center; 
                justify-content: center;
            ">
            <img src="https://implemental.files.wordpress.com/2022/09/en-co-funded-by-the-eu_pos.png?w=300" alt="Cofunded by the European Union" style="
                    width: 150px; 
                    height: auto; 
                    margin-right: 20px;
                    padding-left: 20px;
                    min-width: 150px;
                    max-width: 200px;
            ">
            <p style="
                    text-align: left; 
                    line-height: 1.5;
                    padding-right: 20px;
                    font-size: 0.85em;
                    color: #546e7a;
            ">""" + footer_str_html_langmap[display_language] + """</p>
        </div>
    </footer>
    """,
    styles={
        "margin": "0",
        "padding": "0",
        "position": "fixed",
        "bottom": "0",
        "z-index": "2147483647" # make sure that it always stays on top of everything else in the web page
    }
)
    return footer


#########################
# PRELIMINARY DATA CHECK
#########################

# Here, I should already have the database loaded into a pandas dataframe.
# I should check that the database is not empty, and that it has the correct structure.
# I should also check that the database has the correct values, and that the values 
# are consistent with the data dictionary.
# Part of that is done in the sas_database_reader.py file.
# Here, I just check if I have the database, but if the database has any problem, this is the right time to
# raise an error and stop the execution of the program. 

if DB is None:
    database_not_found_langmap = {
        "en": "Database not found",
        "it": "Database non trovato",
        "fr": "Base de données non trouvée",
        "de": "Datenbank nicht gefunden",
        "es": "Base de datos no encontrada",
        "pt": "Base de dados não encontrada"
    }

    def build_app(language):
        # Change language
        global display_language
        display_language = language
        # Build app
        header = build_header()
        body = panel.pane.HTML(
            """<h1 id="dashboard-body" style="
                    text-align: center; 
                    font-size: 2em; 
                    color: #4a4a4a;
                    padding-bottom: 0;
                    margin-bottom: 0; 
                    margin-top: 30px;
                    font-family: sans-serif;
                    font-weight: 800;
            ">""" + database_not_found_langmap[display_language] + "</h1>",
            styles={
            }
        )
        footer = build_footer()
        return [header, body, footer]

    APP = panel.Column(
        objects = panel.bind(
            build_app, 
            language_selector_widget
        ),
        styles={
            "background": "#ffffffff",
            "width": 'calc(100vw - 17px)',
            "height": "100%"
        }
    )
    APP.show()
    sys.exit(-1)


















####################
# All diseases page
####################


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
    columns = [database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"]]
    columns.extend([diseases_langmap[display_language][d] for d in disturbi])
    df3 = pandas.DataFrame(
        rows_to_add,
        index=year_of_inclusion_list,
        columns=columns
    )
    # x: always the year of inclusion
    # y: the number of patient stratified by disease
    y_labels_langmap = {
        "en": "Number of patients",
        "it": "Numero di pazienti",
        "fr": "Nombre de patients",
        "de": "Anzahl der Patienten",
        "es": "Número de pacientes",
        "pt": "Número de pacientes"
    }
    plot_title_langmap = {
        "en": "Number of patients by year of inclusion, stratified by disease.",
        "it": "Numero di pazienti per anno di inclusione, stratificati per disturbo.",
        "fr": "Nombre de patients par année d'inclusion, stratifiés par maladie.",
        "de": "Anzahl der Patienten nach Jahr der Aufnahme, stratifiziert nach Krankheit.",
        "es": "Número de pacientes por año de inclusión, estratificados por enfermedad.",
        "pt": "Número de pacientes por ano de inclusão, estratificados por doença."
    }
    df3.drop(columns=[diseases_langmap[display_language]["ALL"]], inplace=True)
    # now, we create the overall plot
    # - first, the plot of the number of all patients
    df3_for_plotting = df3.copy()
    df3_for_plotting[y_labels_langmap[display_language]] = df3_for_plotting[[diseases_langmap[display_language][d] for d in disturbi[1:]]].sum(axis=1)
    df3_for_plotting = df3_for_plotting.drop(columns=[diseases_langmap[display_language][d] for d in disturbi[1:]])
    PLOT_COLOR = "blue"
    curve = holoviews.Curve(
        data=df3_for_plotting,
        kdims=[database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"]],
        vdims=[y_labels_langmap[display_language]],
    ).opts(
        color=PLOT_COLOR,
        line_width=1.5
    )
    scatter = holoviews.Scatter(
        data=df3_for_plotting,
        kdims=[database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"]],
        vdims=[y_labels_langmap[display_language]],
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
            'text': [str(a) for a in df3_for_plotting[y_labels_langmap[display_language]]]
        }, 
        ['x', 'y'], 'text'
    ).opts(
        align="center",
        text_font_size='8pt',
        yoffset = max(df3_for_plotting[y_labels_langmap[display_language]])/10,
        text_color="#302070"
    )
    # - here, the barplot with the stacked subdivisions
    df3_melted = pandas.melt(
        df3, 
        id_vars=[database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"]],
        value_vars=[diseases_langmap[display_language][d] for d in disturbi[1:]],
        var_name=disease_word_langauges_map[display_language],
        value_name=y_labels_langmap[display_language]
    )
    bars = holoviews.Bars(
        data=df3_melted,
        kdims=[database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"], disease_word_langauges_map[display_language]],
        vdims=[y_labels_langmap[display_language]],
    ).opts(
        stacked=True,
        legend_position="bottom_left",
        tools=["hover"],
        
    )
    # - composite plot
    plot = (bars * curve * scatter * text_labels).opts(
        xlabel=database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"],
        ylabel=y_labels_langmap[display_language],
        title=plot_title_langmap[display_language],
        ylim=(
            0, 
            (5/4)*df3_for_plotting[y_labels_langmap[display_language]].max()
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

def get_plot__binding_callback(df_clean, sex_selector_widget, age_range_selector_widget, age_range_min_max):    ### THIS FUNCTION IS NOT YET READY TO BE MULTILINGUAL
        # make a plot with x: year of inclusion, y: indicator value, considering the provided stratification
        x = [int(y) for y in list(set(df_clean["ANNO_DI_INCLUSIONE"]))]
        x.sort()
        # BIOLOGICAL SEX STRATIFICATION DEPENDANT PLOT
        # A different plot for each sex selection, choosing from: ["M", "F", "M and F", "Unk.", "All"]
        # Now, for M, F, Unk. and All, the plot is basically, the same, but with different colors.
        color_map = {
            "M": "navy",
            "F": "purple",
            "Unk.": "gray",
            "All": "blue"
        }
        MF_SCATTER_LINE_COLOR = "#202020"
        M_AREA_COLOR = "#c5ddf7a0"
        F_AREA_COLOR = "#ffcecea0"
        common_options = {
            "xlabel":     database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"],
            "ylabel":     indicator_value_langmap[display_language],
            "yformatter": '%d%%',
            "title":      indicator_plot_title_langmap[display_language],
            "show_grid":  True,
            "xlim":       (min(x)-0.5, max(x)+0.5),
            "ylim":       (0, 100)
        }
        if sex_selector_widget in ["M", "F", "Unk.", "All"]:
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
            curve = holoviews.Curve(
                data=pandas.DataFrame({"x": x, "y": 100*y}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Indicator value (%)")]
            ).opts(
                color=color_map[sex_selector_widget],
                tools=[],
            )
            scatter = holoviews.Scatter(
                data=pandas.DataFrame({"x": x, "y": 100*y}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Indicator value (%)")]
            ).opts(
                size=10, 
                fill_color='white', 
                line_color=color_map[sex_selector_widget], 
                line_width=1.5,
                tools=["hover"]
            )
            plot = (curve * scatter).opts(
                **common_options
            )
            return plot
        elif sex_selector_widget == "M and F":
            # Now, we want to have a plot like the one above, but
            # we also want an area coloring the proportion of males and females
            # in the total number of patients.
            y = []
            ym, ym_proportion = [], []
            yf, yf_proportion = [], []
            for year in x:
                # M and F indicator
                numerator_mf, denominator_mf = (numpy.sum(a) for a in get_clean_dataframe_filters_for_numerator_and_denominator(df_clean, year, sex_selector_widget, age_range_selector_widget, age_range_min_max))
                if denominator_mf == 0:
                    y.append(0)
                else:
                    y.append(numerator_mf / denominator_mf)
                # Contribution of each sex to the MF percentage
                numerator_m, denominator_m = (numpy.sum(a) for a in get_clean_dataframe_filters_for_numerator_and_denominator(df_clean, year, "M", age_range_selector_widget, age_range_min_max))
                numerator_f, denominator_f = (numpy.sum(a) for a in get_clean_dataframe_filters_for_numerator_and_denominator(df_clean, year, "F", age_range_selector_widget, age_range_min_max))
                if numerator_mf == 0:
                    y_m = 0
                    y_f = 0
                else:
                    # her, i divide by the numerator, because what i want to display is not the
                    # indicator computed with just M or F over all M and F, but I want the proportion
                    # of M or F over all M and F that contribute to the indicator numerator.
                    # 
                    # es: if the indicator is the number of patients with at least one intervention,
                    # with the area plots I want to represent how much M or F contribute to the total
                    # of the numerator, not the proportion of M or F over all M and F. This should be
                    # a much useful insight.
                    y_m = numerator_m / numerator_mf
                    y_f = numerator_f / numerator_mf
                ym_proportion.append(y_m) # This is the actual mathematical value I'm interested in,
                yf_proportion.append(y_f) #  to be displayed in the hover tooltip
                ym.append(y_m*y[-1])      # This is the value I need to make the area plot
                yf.append(y_f*y[-1])
            # convert to numpy arrays
            x = numpy.array(x)
            y = numpy.array(y)
            ym, ym_proportion = numpy.array(ym), numpy.array(ym_proportion).astype(float)
            yf, yf_proportion = numpy.array(yf), numpy.array(yf_proportion).astype(float)
            # first make the area
            area_m = holoviews.Area(
                data=pandas.DataFrame({"x": x, "y": 100*ym}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Proportion of males (%)")],
            ).opts(
                color=M_AREA_COLOR,
                line_width=0
            )
            area_f = holoviews.Area(
                data=pandas.DataFrame({"x": x, "y": 100*yf}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Proportion of females (%)")],
            ).opts(
                color=F_AREA_COLOR,
                line_width=0
            )
            area = holoviews.Area.stack(
                holoviews.Overlay([area_m, area_f])
            )
            # make a scatterplot at top of female area with, for each point,
            # when you hover on it, tells the proportion of males and females
            males_prop_text = proportions_text_plot_indicator_area_hover_langmap[display_language]["M"]
            female_prop_text = proportions_text_plot_indicator_area_hover_langmap[display_language]["F"]
            custom_tooltips = bokeh.models.HoverTool(
                tooltips=[
                    (database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"], "@x"),
                    (males_prop_text, "@males_prop %"),
                    (female_prop_text, "@females_prop %")
                ]
            )
            area_tooltip_scatter = holoviews.Points(
                data=pandas.DataFrame(
                    {
                        "x": x.tolist(),                                    # x axis location
                        "y": (100*ym).tolist(),                             # y axis location
                        "males_prop": (100*ym_proportion).tolist(),         # only in hover tooltip
                        "females_prop": (100*yf_proportion).tolist()         # only in hover tooltip
                    },
                ),
                kdims=["x", "y"],
                vdims=["males_prop","females_prop"]
            ).opts(
                size=5,
                fill_color="white",
                hover_fill_color="gray",
                line_width=0,
                tools=[custom_tooltips]
            )
            # make the MF plot
            curve = holoviews.Curve(
                data=pandas.DataFrame({"x": x, "y": 100*y}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Indicator value (%)")]
            ).opts(
                color=MF_SCATTER_LINE_COLOR,
                tools=[],
                #line_width=2.5
            )
            scatter = holoviews.Scatter(
                data=pandas.DataFrame({"x": x, "y": 100*y}),
                kdims=[("x", "Year of inclusion")],
                vdims=[("y", "Indicator value (%)")]
            ).opts(
                size=10, 
                fill_color='white', 
                line_color=MF_SCATTER_LINE_COLOR, 
                line_width=2.5,
                tools=["hover"]
            )
            plot = (area * area_tooltip_scatter * curve * scatter).opts(
                **common_options
            )
            return plot
        else:
            raise RuntimeError("This should never happen. Choose a valid sex selection option.")

def get_dataframe_for_tabulator__binding_callback(df_clean: pandas.DataFrame, sex_selector_widget, age_range_selector_widget, age_range_min_max):
    df_clean = df_clean.copy() # so we detach from the original dataframe
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

def get_box_element(df_global, disease: str, cohort: str, indicator: str):
    """ The box element is a row, containing a column with title, description of the indicator,
        a row with a plot and a table side by side, and widgets to interact with the plot and the table.
    """
    df = clean_global_dataframe_by_disease_cohort_indicator(df_global, disease, cohort, indicator)
    # - title
    ind_text_, ind_num_ = tuple(indicator.split(" ")) # "Indicatore 1" -> "Indicatore" -> "Indicator"
    ind_text_t_ = indicator_langmap_it[display_language][ind_text_]
    indicator_text_title = ind_text_t_ + " " + ind_num_
    title_panel = panel.panel(
        """<h1 style="
                text-align: left; 
                font-size: 1.2em; 
                color: #4a4a4a;
                padding-bottom: 0;
                margin-bottom: 0; 
        ">""" + indicator_text_title + "</h1>",
        styles={
        }
    )
    # - description
    description_panel = panel.panel(
        """<p style="
                text-align: left;
                color: #546e7a;
                font-size: 0.7em;
                margin-top: -1.0em;
                margin-bottom: 0.0em;
                padding-top: 0;
                padding-bottom: 0;
        ">(Optional) description of the indicator (yet to be translated)</p>""",
        styles={
        }
    )
    # widgets - sex selector
    sex_selector_widget = panel.widgets.Select(
        name=database_keys_langmap[display_language]["SESSO"],
        value="All",
        options={ # key -> value displayed in web page, value -> value passed to the callback
            sex_selector_langmap[display_language]["M"]: "M", 
            sex_selector_langmap[display_language]["F"]: "F", 
            sex_selector_langmap[display_language]["M and F"]: "M and F", 
            sex_selector_langmap[display_language]["Unk."]: "Unk.", 
            sex_selector_langmap[display_language]["All"]: "All"
        }
    )
    # widgets - age selector
    age_min = max(3, min([int(y) for y in df["AGE"] if y != "Unk."]))
    age_max = max(90, max([int(y) for y in df["AGE"] if y != "Unk."]))
    age_range_selector_widget = panel.widgets.RangeSlider(
        name=age_range_langmap[display_language], 
        start=age_min, 
        end=age_max,
        value=(20, 30),
        step=1,
        #format=bokeh.models.formatters.PrintfTickFormatter(
        #    format='%d '+years_old_langmap[display_language]
        #)
        format = bokeh.models.formatters.CustomJSTickFormatter(
            # https://docs.bokeh.org/en/latest/docs/reference/models/formatters.html#bokeh.models.CustomJSTickFormatter
            code="""
            let disp_num = Math.round(tick);
            disp_num = disp_num.toString();
            let text = disp_num + ' """+years_old_langmap[display_language]+"""';
            return text;
            """
        )
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
    ############### the code in these lines has been added only for demonstartion purposes to show that an indicator can be based on anything
    indicator_type_langmap = {
        "en": {
            0: "Number of interventions",
            1: "Adherence score",
            2: "Percieved subjective benefit",
            3: "Pain score"
        },
        "it": {
            0: "Numero di interventi",
            1: "Punteggio di aderenza",
            2: "Beneficio soggettivo percepito",
            3: "Punteggio del dolore"
        },
        "fr": {
            0: "Nombre d'interventions",
            1: "Score d'adhérence",
            2: "Bénéfice subjectif perçu",
            3: "Score de douleur"
        },
        "de": {
            0: "Anzahl der Interventionen",
            1: "Adhärenz-Score",
            2: "Wahrgenommener subjektiver Nutzen",
            3: "Schmerz-Score"
        }, 
        "es": {
            0: "Número de intervenciones",
            1: "Puntuación de adherencia",
            2: "Beneficio subjetivo percibido",
            3: "Puntuación del dolor"
        },
        "pt": {
            0: "Número de intervenções",
            1: "Pontuação de adesão",
            2: "Benefício subjetivo percebido",
            3: "Pontuação da dor"
        }
    }
    global indicator_type_langmap_chooser
    ####################################################################
    table_widget = panel.widgets.Tabulator(
        panel.bind(
            get_dataframe_for_tabulator__binding_callback,
            df_clean=df,
            sex_selector_widget=sex_selector_widget,
            age_range_selector_widget=age_range_selector_widget,
            age_range_min_max=(age_min, age_max)
        ),
        theme='simple',
        pagination='remote', 
        page_size=10,
        formatters={
            # formatters (dict): A dictionary mapping from column name to a bokeh CellFormatter instance
            # or Tabulator formatter specification.
            # https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html
            "ANNO_DI_INCLUSIONE": bokeh.models.NumberFormatter(format="0"),
            "TOT_INTERVENTI": bokeh.models.NumberFormatter(format="0"),
            "AGE": bokeh.models.NumberFormatter(format="0")
        },
        text_align="left",
        titles={
            # titles (dict): A dictionary mapping from column name to a string to use as the column title.
            "ANNO_DI_INCLUSIONE": database_keys_langmap[display_language]["ANNO_DI_INCLUSIONE"],
            "SESSO": database_keys_langmap[display_language]["SESSO"],
            "TOT_INTERVENTI": indicator_type_langmap[display_language][indicator_type_langmap_chooser], # database_keys_langmap[display_language]["TOT_INTERVENTI"],
            "AGE": database_keys_langmap[display_language]["AGE"]
        },
        show_index=False
    )
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
        #
        sizing_mode='stretch_both',
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

def disease_selector_row_title_maker(value):
    if value is None:
        value = """<span style="font-size: 1.1em; color: #888888ff;">
                """+default_title_message_langmap[display_language]+"""
                </span>"""
    if value == diseases_langmap[display_language]["ALL"]:
        value = all_diseases_title_message_langmap[display_language]
    text = """<h1>"""+value+"</h1>"
    html_pane = panel.pane.HTML(
        text,
        styles={
            "margin-left": "1.5em"
        }
    )
    return html_pane

def build_body_disease_selector():
    disturbi = list(set(DB["DISTURBO"]))
    disturbi.sort()
    disturbi = numpy.insert(disturbi, 0, "ALL")
    title_choice_map = {diseases_langmap[display_language][k]: diseases_langmap[display_language][k] for k in disturbi}
    title_menu_items = [(k, v) for k, v in title_choice_map.items()]
    # title menu button
    global title_menu_button
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
    # make the whole row
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
    return disease_selector_row


# COORTE SELECTOR

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

def build_body_coorte_selector():
    # buttons coorte selector
    coorte_button_options_list = [
        v for v in coorte_explain_dict[display_language].keys()
    ]
    global coorte_radio_group                                       ### THIS IS NOT A GOOD IDEA but i have to make it work
    coorte_radio_group = panel.widgets.RadioButtonGroup(
        name='coorte selector', 
        options=coorte_button_options_list, 
        value=coorte_button_options_list[0],
        button_type='primary'
    )
    # 
    coorte_selector_row = panel.Column(
        coorte_radio_group,
        panel.bind(update_coorte_html, coorte_radio_group.param.value)
    )
    return coorte_selector_row

def build_body_top_row():
    disease_selector_row = build_body_disease_selector()
    # coorte_selector_row = build_body_coorte_selector()    # This was moved from hete to inside the tabs in which to select the indicator type
    #                                                         This because some indicators are of one type and require a coorte selector (evaluation),
    #                                                         while others are of another type and do not require a coorte selector (monitoring).
    top_selector_row = panel.Column(
        disease_selector_row,
        #coorte_selector_row,
        styles={
            "margin-top": "0px",
            "padding-top": "0px",
            "margin-bottom": "5px",
            "background": "#e9ecefff",
            "border-radius": "16px"
        }
    )
    return top_selector_row







# - MAIN BODY - PLOTS AND TABLES

global indicator_type_langmap_buffer   ### those two are a quick fix to show, in the table in the UI, different names and not
global indicator_type_langmap_chooser  ###  always just "Number of interventions". This is just for demonstration purposes.

indicator_type_langmap_buffer = {k: [] for k in diseases_langmap[display_language]} # keys: BIPO, SCHIZO, .... language independant

def get_main_box_elements(df, disease_selector_value, coorte_selector_value):
    if disease_selector_value == diseases_langmap[display_language]["ALL"]:
        return [
            panel.bind(plot_all_diseases_by_year_of_inclusion, DB, coorte_radio_group.param.value)
        ]
    else:
        # clean input
        disease_selector_value = dict_find_key_by_value(diseases_langmap[display_language], disease_selector_value)
        coorte_selector_value = str(coorte_selector_value)[-1].upper()
        # find list of all indicators available for that disease and cohort
        list_of_boxes_to_display = []
        selection = (df["DISTURBO"] == disease_selector_value)
        selection = selection & (df["COORTE"] == coorte_selector_value)
        indicators = list(set(df.loc[selection,"INDICATORE"]))
        indicators.sort()
        #   ###########################################################################
        #   #   THIS IS A QUICK FIX TO SHOW DIFFERENT NAMES IN THE TABLE IN THE UI    #
        global indicator_type_langmap_buffer, indicator_type_langmap_chooser
        if len(indicator_type_langmap_buffer[disease_selector_value]) == 0:
            # first time entering the function -> create a list of names to dysplay in the table
            indicator_type_langmap_buffer[disease_selector_value] = numpy.random.randint(0, 4, len(indicators)).tolist()
        # get all plots and elements
        for i_, indicator in enumerate(indicators):
            indicator_type_langmap_chooser = indicator_type_langmap_buffer[disease_selector_value][i_]
            list_of_boxes_to_display.append(
                get_box_element(df, disease_selector_value, coorte_selector_value, indicator)
            )
        # add a final spacer to make room for the page footer
        list_of_boxes_to_display.append(
            panel.Spacer(height=100)
        )
        return list_of_boxes_to_display
    
def build_body_main_box():             ##########    qui vanno aggiunte le due tab per i due tipi di indicatori
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
    return main_box



#########################################################
# Create tabs for the two different types of indicators:
# - monitoring
# - evaluation (needs the coorte selector)
#########################################################

def build_monitoring_indicators_tab():
    body = panel.Column(
        build_body_main_box(),
        panel.Spacer(height=50),
        styles={
            "margin-top": "20px",
            "padding-top": "0px",
            "margin-bottom": "35px"
        }
    )
    return body

def build_evaluation_indicators_tab():
    body = panel.Column(
        build_body_coorte_selector(),
        build_body_main_box(),
        panel.Spacer(height=50),
        styles={
            "margin-top": "20px",
            "padding-top": "0px",
            "margin-bottom": "35px"
        }
    )
    return body

evaluation_indicators_langmap = {
    "en": "Evaluation indicators",
    "it": "Indicatori di valutazione",
    "fr": "Indicateurs d'évaluation",
    "de": "Bewertungsindikatoren",
    "es": "Indicadores de evaluación",
    "pt": "Indicadores de avaliação"
}
monitoring_indicators_langmap = {
    "en": "Monitoring indicators",
    "it": "Indicatori di monitoraggio",
    "fr": "Indicateurs de surveillance",
    "de": "Überwachungsindikatoren",
    "es": "Indicadores de monitoreo",
    "pt": "Indicadores de monitoramento"
}

from panel.theme import Material

def build_indicator_type_tabs():
    tab_evaluation = build_evaluation_indicators_tab() # evaluation is created before monitoring because it needs the coorte selector, otherwise the build_body_main_box() cannot access coorte_selector_value=coorte_radio_group.param.value . This is poor design but it is just a quick fix for the UI.
    tab_monitoring = build_monitoring_indicators_tab()
    style_sheet = """
        :host(.bk-above) {
            # to modify all the tab ememnts (or, the elemnt inside the tab div)
        }
        :host(.bk-above) .bk-header{
            # to modify the header of the tab
        }
        :host(.bk-above) .bk-header .bk-tab {
            border-bottom-width: 4px;
            color: #909090ff;
            border-bottom-color: #909090ff;
        }
        :host(.bk-above) .bk-header .bk-tab.bk-active {
            background: #0072b5ff;
            color: #fafafaff;
            font-weight: bold;
            border-bottom-color: #025383ff;
        }
    """
    # https://panel.holoviz.org/how_to/styling/apply_css.html
    tabs = panel.Tabs(
        (monitoring_indicators_langmap[display_language], tab_monitoring),
        (evaluation_indicators_langmap[display_language], tab_evaluation),
        tabs_location="above",
        active=0,
        styles={
            "margin-top": "0px",
            "padding-top": "0px",
            "margin-bottom": "35px",
            "--pn-tab-active-color": "#ff1155ff"
        },
        design=Material,
        stylesheets=[style_sheet]
    )
    return tabs




# - BODY
def build_body():               
    body = panel.Column(
        build_body_top_row(),
        build_indicator_type_tabs(),  # instead of build_body_main_box()
        panel.Spacer(height=50),
        styles={
            "margin-top": "20px",
            "padding-top": "0px",
            "margin-bottom": "35px"
        }
    )
    return body





###############            inspiration for next UI:
#
#       https://awesome-panel.org/resources/hurdat_tracks_viewer/
#
#       https://huggingface.co/spaces/ahuang11/hurdat_tracks_viewer/blob/main/app.py 
#
#       how is this code so clean???
#
# So good, also use tabs for data, so you can see plots bigger, and also the table bigger
# and in the remainins space you could insert an explanation of the indicator maybe







##################
# Dashboard
##################

# LANGUAGE WIDGET:
# The languagw widget, defined before the header, 
# is a widget that allows the user to change the language of the dashboard.
# as of now, since we do not want to re-write the whole code,
# we will reload the whole page when the language is changed.
#
# To do so, here i define all the builders for the different parts of the dashboard,
# whch are the header, the body and the footer.
# This structure was thought AFTER developing all the dashboard, so it is not
# the best structure, but it is the one I have now. If code needed to be refactored,
# this would be the first thing to do, to create builders of each component of the dashboard
# so they can be plugged in together easily. Also using a global variable is usually a thrash idea.
#
# The various builders are spread here and there n the code, in the pertinent sections.
# Down here, I just have the build_all function which calls all the builders and returns
# the three components of the dashboard.

def build_all(language_value):
    # update the global variable to change language
    global display_language
    if language_value in AVAILABLE_LANGUAGES:
        display_language = language_value
    else:
        display_language = "en"
    # build the app again
    header = build_header()
    body = build_body()
    footer = build_footer()
    return [header, body, footer]


    
APP = panel.Column(
        objects = panel.bind(
            build_all, 
            language_selector_widget
        ),
        styles={
            "background": "#ffffffff",
            "width": 'calc(100vw - 17px)',
            "height": "100%",
            "scroll-behavior": "smooth"
        }
    )


APP.show()