import os
import pandas
import bokeh.palettes

FILES_FOLDER = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia restricted\\"

DEMOGRAPHICS_DB_FILENAME = "demographics_restr.sas7bdat"
DIAGNOSES_DB_FILENAME = "diagnoses_restr.sas7bdat"
INTERVENTIONS_DB_FILENAME = "interventions_restr.sas7bdat"
PHARMA_DB_FILENAME = "pharma_restr.sas7bdat"
PHYSICAL_EXAMS_DB_FILENAME = "physical_exams_restr.sas7bdat"

COHORST_DB_FILENAME = "cohorts.sas7bdat"


############
# CONSTANTS
############

DISEASE_CODE_TO_DB_CODE = {
    "_schizophrenia_": "SCHIZO",
    "_depression_": "DEPRE",
    "_bipolar_disorder_": "BIPOLAR"
}

COHORT_CODE_TO_DB_CODE = {
    "_a_": "INCIDENT",
    "_b_": "PREVALENT",
    "_c_": "INCIDENT_1825"
}

INTERVENTIONS_CODES_LANGDICT_MAP = {
    "en": {
        "01": {
            "legend": "Psychiatric visit",
            "short": "Psychiatric visit",
            "long": 
                """
                Psychiatric visit (i.e., psychiatric visits, 
                physician's visits, visits for Medico-legal assessment, 
                opinion visits in the General Hospital, 
                individual meeting with a professional, consultation)	
                """
        },
        "02": {
            "legend": "Psychological assessment",
            "short": "Standardized psychological assessment using test",
            "long": 
                """
                Standardized psychological assessment using test
                (i.e., Standardized psychological assessments using test)	
                """
        },
        "03": {
            "legend": "Home visit",
            "short": "Home visit",
            "long": 
                """
                Home visit (i.e., home nursing activity, home visits, etc)	
                """
        },
        "04": {
            "legend": "Psychosocial intervention",
            "short": "Psychosocial intervention",
            "long": 
                """
                Psychosocial intervention
                (i.e., Individual living skills training, Group living skills training,
                Individual socialization, Individual socialization, Group of socialization, 
                Individual or Group bodywork - i.e., expressive, practical manual and motor intervention, -
                leisure activities, Support to daily living activity,
                Assistance with financial and welfare procedures)	
                """
        },
        "05": {
            "legend": "Psychoeducation session",
            "short": "Psychoeducation session",
            "long": 
                """
                Psychoeducation session (i.e., Single family psychoeducation, 
                Multifamily group psychoeducation)	
                """
        },
        "06": {
            "legend": "Psychotherapy session",
            "short": "Psychotherapy session",
            "long": 
                """
                Psychotherapy session (i.e., Psychological visit, 
                Individual psychotherapy, Couple psychotherapy, 
                Family psychotherapy, Group psychotherapy)	
                """
        },
        "07": {
            "legend": "Interventions to family members",
            "short": "Contact or interventions addressed to patients' family members",
            "long": 
                """
                Outpatient carers' contact or intervention 
                specifically addressed to patients' family members 
                (i.e., Meeting with relatives, Family psychotherapy, Multifamily group psychoeducation)	
                """
        },
        "Other": {
            "legend": "Other",
            "short": "Other",
            "long": 
                """
                Other mental health interventions
                (i.e., Staff Meeting, Healthcare facilities stay, 
                Vocational training, Network interventions) 	
                """
        }
    },
    "it": {
        "01": {
            "legend": "Visita psichiatrica",
            "short": "Visita psichiatrica",
            "long": 
                """
                Visita psichiatrica (es. visite psichiatriche, 
                visite mediche, visite per accertamenti medico-legali, 
                visite di consulenza in Ospedale Generale, 
                incontri individuali con un professionista, consulto)	
                """
        },
        "02": {
            "legend": "Valutazione psicologica",
            "short": "Valutazione psicologica standardizzata con test",
            "long": 
                """
                Valutazione psicologica standardizzata con test
                (es. Valutazioni psicologiche standardizzate con test)	
                """
        },
        "03": {
            "legend": "Visita domiciliare",
            "short": "Visita domiciliare",
            "long": 
                """
                Visita domiciliare (es. attività infermieristica domiciliare, 
                visite domiciliari, ecc)	
                """
        },
        "04": {
            "legend": "Intervento psicosociale",
            "short": "Intervento psicosociale",
            "long": 
                """
                Intervento psicosociale
                (es. Training alle abilità di vita individuale, 
                Training alle abilità di vita di gruppo, 
                Socializzazione individuale, Socializzazione di gruppo, 
                Lavoro corporeo individuale o di gruppo - es. intervento espressivo, 
                manuale pratico e motorio, - attività di svago, 
                Supporto all'attività quotidiana, Assistenza alle procedure finanziarie e assistenziali)	
                """
        },
        "05": {
            "legend": "Sessione di psicoeducazione",
            "short": "Sessione di psicoeducazione",
            "long": 
                """
                Sessione di psicoeducazione (es. Psicoeducazione familiare singola, 
                Psicoeducazione di gruppo multifamiliare)	
                """
        },
        "06": {
            "legend": "Sessione di psicoterapia",
            "short": "Sessione di psicoterapia",
            "long": 
                """
                Sessione di psicoterapia (es. Visita psicologica, 
                Psicoterapia individuale, Psicoterapia di coppia, 
                Psicoterapia familiare, Psicoterapia di gruppo)	
                """
        },
        "07": {
            "legend": "Iinterventi ai familiari",
            "short": "Contatto o interventi rivolti ai familiari dei pazienti",
            "long": 
                """
                Contatto o intervento rivolto ai familiari dei pazienti 
                (es. Incontro con i parenti, Psicoterapia familiare, 
                Psicoeducazione di gruppo multifamiliare)	
                """
        },
        "Other": {
            "legend": "Altro",
            "short": "Altro",
            "long": 
                """
                Altri interventi di salute mentale
                (es. Riunione del personale, Permanenza nelle strutture sanitarie, 
                Formazione professionale, Interventi di rete)	
                """
        }
    },
    "fr": {
        "01": {
            "legend": "Visite psychiatriques",
            "short": "Visite psychiatriques",
            "long": 
                """
                Visites psychiatriques (c'est-à-dire visites psychiatriques, 
                visites médicales, visites pour évaluation médico-légale, 
                visites d'opinion à l'hôpital général, 
                réunion individuelle avec un professionnel, consultation)	
                """
        },
        "02": {
            "legend": "Évaluation psychologique",
            "short": "Évaluation psychologique standardisée à l'aide de tests",
            "long": 
                """
                Évaluation psychologique standardisée à l'aide de tests
                (c'est-à-dire évaluations psychologiques standardisées à l'aide de tests)	
                """
        },
        "03": {
            "legend": "Visite à domicile",
            "short": "Visite à domicile",
            "long": 
                """
                Visite à domicile (c'est-à-dire activité de soins infirmiers à domicile, 
                visites à domicile, etc.)	
                """
        },
        "04": {
            "legend": "Intervention psychosociale",
            "short": "Intervention psychosociale",
            "long": 
                """
                Intervention psychosociale
                (c'est-à-dire formation aux compétences de vie individuelle, formation aux compétences de vie de groupe, 
                socialisation individuelle, socialisation de groupe, 
                travail corporel individuel ou de groupe - c'est-à-dire intervention expressive, 
                manuelle pratique et motrice, - activités de loisirs, 
                soutien aux activités quotidiennes, assistance aux procédures financières et d'aide)	
                """
        },
        "05": {
            "legend": "Séance de psychoéducation",
            "short": "Séance de psychoéducation",
            "long": 
                """
                Séance de psychoéducation (c'est-à-dire psychoéducation familiale individuelle, 
                psychoéducation de groupe multifamiliale)	
                """
        },
        "06": {
            "legend": "Séance de psychothérapie",
            "short": "Séance de psychothérapie",
            "long": 
                """
                Séance de psychothérapie (c'est-à-dire visite psychologique, 
                psychothérapie individuelle, psychothérapie de couple, 
                psychothérapie familiale, psychothérapie de groupe)	
                """
        },
        "07": {
            "legend": "Interventions aux la famille",
            "short": "Contact ou interventions adressés aux membres de la famille des patients",
            "long": 
                """
                Contact ou intervention des aidants à domicile 
                spécifiquement adressé aux membres de la famille des patients 
                (c'est-à-dire rencontre avec les proches, psychothérapie familiale, psychoéducation de groupe multifamiliale)	
                """
        },
        "Other": {
            "legend": "Autre",
            "short": "Autre",
            "long": 
                """
                Autres interventions en santé mentale
                (c'est-à-dire réunion du personnel, séjour dans les établissements de santé, 
                formation professionnelle, interventions en réseau)	
                """
        }
    },
    "de": {
        "01": {
            "legend": "Psychiatrische Untersuchung",
            "short": "Psychiatrische Untersuchung",
            "long": 
                """
                Psychiatrische Untersuchung (d.h. psychiatrische Untersuchungen, 
                Arztbesuche, Besuche zur medizinisch-legalen Beurteilung, 
                Meinungsbesuche im Allgemeinkrankenhaus, 
                Einzelgespräche mit einem Fachmann, Beratung)	
                """
        },
        "02": {
            "legend": "Psychologische Bewertung",
            "short": "Standardisierte psychologische Bewertung mit Test",
            "long": 
                """
                Standardisierte psychologische Bewertung mit Test
                (d.h. standardisierte psychologische Bewertungen mit Test)	
                """
        },
        "03": {
            "legend": "Hausbesuch",
            "short": "Hausbesuch",
            "long": 
                """
                Hausbesuch (d.h. häusliche Krankenpflege, 
                Hausbesuche, etc.)	
                """
        },
        "04": {
            "legend": "Psychosoziale Intervention",
            "short": "Psychosoziale Intervention",
            "long": 
                """
                Psychosoziale Intervention
                (d.h. Training in individuellen Lebenskompetenzen, Training in Gruppenlebenskompetenzen, 
                Individuelle Sozialisierung, Gruppensozialisierung, 
                Individuelle oder Gruppenkörperarbeit - d.h. expressive, praktische manuelle und motorische Intervention, - 
                Freizeitaktivitäten, Unterstützung bei täglichen Lebensaktivitäten, 
                Unterstützung bei finanziellen und sozialen Verfahren)	
                """
        },
        "05": {
            "legend": "Psychoedukationssitzung",
            "short": "Psychoedukationssitzung",
            "long": 
                """
                Psychoedukationssitzung (d.h. Einzelfamilienpsychoedukation, 
                Multifamilien-Gruppenpsychoedukation)	
                """
        },
        "06": {
            "legend": "Psychotherapiesitzung",
            "short": "Psychotherapiesitzung",
            "long": 
                """
                Psychotherapiesitzung (d.h. psychologische Untersuchung, 
                Einzeltherapie, Paartherapie, 
                Familientherapie, Gruppentherapie)	
                """
        },
        "07": {
            "legend": "Interventionen für Familienmitglieder",
            "short": "Kontakt oder Interventionen für Familienmitglieder der Patienten",
            "long": 
                """
                Ambulante Pflegekontakt oder Intervention 
                speziell für Familienmitglieder der Patienten 
                (d.h. Treffen mit Verwandten, Familientherapie, Multifamilien-Gruppenpsychoedukation)	
                """
        },
        "Other": {
            "legend": "Andere",
            "short": "Andere",
            "long": 
                """
                Andere psychische Gesundheitsinterventionen
                (d.h. Personalbesprechung, Aufenthalt in Gesundheitseinrichtungen, 
                Berufsausbildung, Netzwerkinterventionen)	
                """
        }
    },
    "es": {
        "01": {
            "legend": "Visita psiquiátrica",
            "short": "Visita psiquiátrica",
            "long": 
                """
                Visita psiquiátrica (es decir, visitas psiquiátricas, 
                visitas médicas, visitas para evaluación médico-legal, 
                visitas de opinión en el Hospital General, 
                reunión individual con un profesional, consulta)	
                """
        },
        "02": {
            "legend": "Evaluación psicológica",
            "short": "Evaluación psicológica estandarizada con test",
            "long": 
                """
                Evaluación psicológica estandarizada con test
                (es decir, evaluaciones psicológicas estandarizadas con test)	
                """
        },
        "03": {
            "legend": "Visita domiciliaria",
            "short": "Visita domiciliaria",
            "long": 
                """
                Visita domiciliaria (es decir, actividad de enfermería domiciliaria, 
                visitas domiciliarias, etc.)	
                """
        },
        "04": {
            "legend": "Intervención psicosocial",
            "short": "Intervención psicosocial",
            "long": 
                """
                Intervención psicosocial
                (es decir, entrenamiento en habilidades de vida individuales, entrenamiento en habilidades de vida en grupo, 
                socialización individual, socialización en grupo, 
                trabajo corporal individual o grupal - es decir, intervención expresiva, 
                manual práctico y motor, - actividades de ocio, 
                apoyo a las actividades diarias, asistencia en procedimientos financieros y de ayuda)	
                """
        },
        "05": {
            "legend": "Sesión de psicoeducación",
            "short": "Sesión de psicoeducación",
            "long": 
                """
                Sesión de psicoeducación (es decir, psicoeducación familiar individual, 
                psicoeducación de grupo multifamiliar)	
                """
        },
        "06": {
            "legend": "Sesión de psicoterapia",
            "short": "Sesión de psicoterapia",
            "long": 
                """
                Sesión de psicoterapia (es decir, visita psicológica, 
                psicoterapia individual, psicoterapia de pareja, 
                psicoterapia familiar, psicoterapia de grupo)	
                """
        },
        "07": {
            "legend": "Intervenciones a los familiares",
            "short": "Contacto o intervenciones dirigidas a los familiares de los pacientes",
            "long": 
                """
                Contacto o intervención de cuidadores en el hogar 
                específicamente dirigido a los familiares de los pacientes 
                (es decir, reunión con familiares, psicoterapia familiar, psicoeducación de grupo multifamiliar)	
                """
        },
        "Other": {
            "legend": "Otro",
            "short": "Otro",
            "long": 
                """
                Otras intervenciones de salud mental
                (es decir, reunión de personal, estancia en instalaciones de salud, 
                formación profesional, intervenciones en red)	
                """
        }
    },
    "pt": {
        "01": {
            "legend": "Visita psiquiátrica",
            "short": "Visita psiquiátrica",
            "long": 
                """
                Visita psiquiátrica (ou seja, visitas psiquiátricas, 
                visitas médicas, visitas para avaliação médico-legal, 
                visitas de opinião no Hospital Geral, 
                reunião individual com um profissional, consulta)	
                """
        },
        "02": {
            "legend": "Avaliação psicológica",
            "short": "Avaliação psicológica padronizada com teste",
            "long": 
                """
                Avaliação psicológica padronizada com teste
                (ou seja, avaliações psicológicas padronizadas com teste)	
                """
        },
        "03": {
            "legend": "Visita domiciliar",
            "short": "Visita domiciliar",
            "long": 
                """
                Visita domiciliar (ou seja, atividade de enfermagem domiciliar, 
                visitas domiciliares, etc.)	
                """
        },
        "04": {
            "legend": "Intervenção psicossocial",
            "short": "Intervenção psicossocial",
            "long": 
                """
                Intervenção psicossocial
                (ou seja, treinamento em habilidades de vida individual, treinamento em habilidades de vida em grupo, 
                socialização individual, socialização em grupo, 
                trabalho corporal individual ou de grupo - ou seja, intervenção expressiva, 
                manual prático e motor, - atividades de lazer, 
                apoio às atividades diárias, assistência em procedimentos financeiros e de ajuda)	
                """
        },
        "05": {
            "legend": "Sessão de psicoeducação",
            "short": "Sessão de psicoeducação",
            "long": 
                """
                Sessão de psicoeducação (ou seja, psicoeducação familiar individual, 
                psicoeducação de grupo multifamiliar)	
                """
        },
        "06": {
            "legend": "Sessão de psicoterapia",
            "short": "Sessão de psicoterapia",
            "long": 
                """
                Sessão de psicoterapia (ou seja, visita psicológica, 
                psicoterapia individual, psicoterapia de casal, 
                psicoterapia familiar, psicoterapia de grupo)	
                """
        },
        "07": {
            "legend": "Intervenções aos familiares",
            "short": "Contato ou intervenções dirigidos aos familiares dos pacientes",
            "long": 
                """
                Contato ou intervenção de cuidadores domiciliares 
                especificamente dirigidos aos familiares dos pacientes 
                (ou seja, encontro com parentes, psicoterapia familiar, psicoeducação de grupo multifamiliar)	
                """
        },
        "Other": {
            "legend": "Outro",
            "short": "Outro",
            "long": 
                """
                Outras intervenções em saúde mental
                (ou seja, reunião de pessoal, estadia em instalações de saúde, 
                formação profissional, intervenções em rede)	
                """
        }
    }
}
# colors

INTERVENTIONS_CODES_COLOR_DICT = {
    "All": "#a0a0a0ff",
    "01": bokeh.palettes.Muted8[0],
    "02": bokeh.palettes.Muted8[1],
    "03": bokeh.palettes.Muted8[2],
    "04": bokeh.palettes.Muted8[3],
    "05": bokeh.palettes.Muted8[4],
    "06": bokeh.palettes.Muted8[5],
    "07": bokeh.palettes.Muted8[6],
    "Other": bokeh.palettes.Muted8[7]
}


#################################
# READ SAS DATABASES WITH PANDAS
#################################

DATABASE_FILENAMES_DICT = {
    "demographics": DEMOGRAPHICS_DB_FILENAME,
    "diagnoses": DIAGNOSES_DB_FILENAME,
    "interventions": INTERVENTIONS_DB_FILENAME,
    "pharma": PHARMA_DB_FILENAME,
    "physical_exams": PHYSICAL_EXAMS_DB_FILENAME,
    "cohorts": COHORST_DB_FILENAME,
}


def read_databases(databases_dict: dict[str: str], files_folder):
    """ Read databases from files and return a dictionary with the dataframes in this format:
    {
        "demographics": dataframe,
        "diagnoses": dataframe,
        "interventions": dataframe,
        "pharma": dataframe,
        "physical_exams": dataframe,
        "cohorts": dataframe,
    }

    Args:
        databases_dict (dict[str: str]): A dictionary with the database names as keys and the filenames as values
        files_folder (str): The folder where the files are stored
    """
    allowed_keys = ["demographics", "diagnoses", "interventions", "pharma", "physical_exams", "cohorts"]
    for k in databases_dict.keys():
        if k not in allowed_keys:
            raise ValueError(f"Key {k} of input dict is not allowed. Allowed keys are {allowed_keys}")
    input_keys_list = list(databases_dict.keys())
    for k in allowed_keys[:-1]:
        # cohorts is not strictly required
        if k not in input_keys_list:
            raise ValueError(f"Key {k} of input dict is missing. Required keys are {allowed_keys[:-1]}")
    db = {}
    for dbkey, f in databases_dict.items():
        file_path = os.path.normpath(FILES_FOLDER + f)
        file_path = file_path.replace("\\", "/").replace("//", "/")
        file_path = os.path.normpath(file_path)
        # Read and parse file content
        df = pandas.read_sas(file_path)
        db[dbkey] = df
    return db


########################
# REDUCE DATABASES SIZE
# - Since databases are quite huge, it would be stupid to compute the indicators on the whole database
# - We need to reduce the size of the databases by selecting only the rows that are compatible with the
# - problem at hand
########################

# to do


##################
# CLEAN DATABASES
##################

class DropNa:
    """Class that is just used as a flag to drop NA values from the dataframes"""
    def __init__(self):
        pass

DATETIME_NAN = pandas.to_datetime("1800-01-01")

def clean_alphanumeric(x: pandas.DataFrame | pandas.Series, fillnan=None) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series
    Alphanumeric
    if fillnan == DropNa class then drop the rows with NaN values
    """
    x_new = pandas.DataFrame(x)
    if fillnan is not None:
        if fillnan == DropNa:
            x_new.dropna(inplace=True)
        else:
            x_new.fillna(fillnan, inplace=True)
    x_new = (
        x_new
        .astype(str)                # from bytes to python strings
        .map(lambda x: x.strip())   # remove leading and trailing empty spaces
    )
    return x_new

def clean_numeric(x: pandas.DataFrame | pandas.Series, dtype: type|None = None, fillnan=None) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series
    Numeric
    if fillnan == DropNa class then drop the rows with NaN values
    """
    x_new = pandas.DataFrame(x)
    if fillnan is not None:
        if fillnan == DropNa:
            x_new.dropna(inplace=True)
        else:
            x_new.fillna(fillnan, inplace=True)
    if dtype is not None:
        x_new = x_new.astype(dtype)
    return x_new

def clean_datetime(x: pandas.DataFrame | pandas.Series) -> pandas.DataFrame | pandas.Series:
    """
    x must be a pandas DataFrame or a pandas Series containing datetime information
    """
    x_new = pandas.DataFrame(x).fillna(DATETIME_NAN)
    for cols in x_new.columns:
        x_new[cols] = pandas.to_datetime(x_new[cols]).astype('datetime64[s]')
    return x_new

def preprocess_cohorts_database(cohort: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Merges and preprocesses the cohorts databases.
    """
    # Merge all the cohorts databases
    if isinstance(cohort, list):
        new = pandas.concat(cohort, axis=0)
    elif isinstance(cohort, pandas.DataFrame):
        new = cohort.copy(deep=True)
    else:
        raise ValueError("cohorts_list must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["YEAR_ENTRY"] = clean_numeric(new["YEAR_ENTRY"], dtype=int, fillnan=DropNa)
    new["PREVALENT"] = clean_alphanumeric(new["PREVALENT"], fillnan=DropNa)
    new["INCIDENT"] = clean_alphanumeric(new["INCIDENT"], fillnan=DropNa)
    new["INCIDENT_1825"] = clean_alphanumeric(new["INCIDENT_1825"], fillnan=DropNa)
    new["SCHIZO"] = clean_alphanumeric(new["SCHIZO"], fillnan="N")
    new["DEPRE"] = clean_alphanumeric(new["DEPRE"], fillnan="N")
    new["BIPOLAR"] = clean_alphanumeric(new["BIPOLAR"], fillnan="N")
    return new

def preprocess_demographics_database(demographics: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Preprocesses the demographics database.
    """
    # Merge all the demographics databases
    if isinstance(demographics, list):
        new = pandas.concat(demographics, axis=0)
    elif isinstance(demographics, pandas.DataFrame):
        new = demographics.copy(deep=True)
    else:
        raise ValueError("demographics must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["DT_BIRTH"] = clean_datetime(new["DT_BIRTH"])
    new["DT_DEATH"] = clean_datetime(new["DT_DEATH"])
    new["CAUSE_DEATH_1"] = clean_alphanumeric(new["CAUSE_DEATH_1"], fillnan="Unknown")
    new["CAUSE_DEATH_2"] = clean_alphanumeric(new["CAUSE_DEATH_2"], fillnan="Unknown")
    new["DT_START_ASSIST"] = clean_datetime(new["DT_START_ASSIST"])
    new["DT_END_ASSIST"] = clean_datetime(new["DT_END_ASSIST"])
    new["GENDER"] = clean_alphanumeric(new["GENDER"], fillnan="U")
    new["CIVIL_STATUS"] = clean_alphanumeric(new["CIVIL_STATUS"], fillnan="Other")
    new["JOB_COND"] = clean_alphanumeric(new["JOB_COND"], fillnan="Unknown")
    new["EDU_LEVEL"] = clean_alphanumeric(new["EDU_LEVEL"], fillnan="Unknown")
    return new

def preprocess_interventions_database(interventions: list[pandas.DataFrame] | pandas.DataFrame) -> pandas.DataFrame:
    """
    Preprocesses the interventions database.
    """
    # Merge all the interventions databases
    if isinstance(interventions, list):
        new = pandas.concat(interventions, axis=0)
    elif isinstance(interventions, pandas.DataFrame):
        new = interventions.copy(deep=True)
    else:
        raise ValueError("interventions must be a list of DataFrame or a DataFrame")
    # Clean
    new["ID_SUBJECT"] = clean_alphanumeric(new["ID_SUBJECT"], fillnan=DropNa)
    new["DT_INT"] = clean_datetime(new["DT_INT"])
    new["TYPE_INT"] = clean_alphanumeric(new["TYPE_INT"], fillnan="Unknown")
    new["STRUCTURE"] = clean_alphanumeric(new["STRUCTURE"], fillnan="Unknown")
    new["OPERATOR_1"] = clean_alphanumeric(new["OPERATOR_1"], fillnan="Unknown")
    new["OPERATOR_2"] = clean_alphanumeric(new["OPERATOR_2"], fillnan="Unknown")
    new["OPERATOR_3"] = clean_alphanumeric(new["OPERATOR_3"], fillnan="Unknown")
    return new






if __name__ == "__main__":
    db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
    db["demographics"] = preprocess_demographics_database(db["demographics"])
    db["interventions"] = preprocess_interventions_database(db["interventions"])
    db["cohorts"] = preprocess_cohorts_database(db["cohorts"])
    print("demographics:\n", db["demographics"].head())
    print("interventions:\n", db["interventions"].head())
    print("cohorts:\n", db["cohorts"].head())