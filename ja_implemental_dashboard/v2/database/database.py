import os, time, datetime
import hashlib
import pandas
import bokeh.palettes
import sqlite3


#############
# CACHING
#############
def get_cache_folder() -> str:
    """ Get the path to the cache folder.
    Returns the path to the cache folder.
    """
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "cache"))


##################################
# USER SELECTION OF DATABASE PATH
##################################

# DATABASE_FILE = os.path.normpath(
#     "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/Dati QUADIM - Standardizzati - Sicilia/DATABASE.sqlite3"
# )

import tkinter
from tkinter import filedialog
root = tkinter.Tk()
root.withdraw()

filedialog_cache_file = os.path.join(get_cache_folder(), "filedialog_last_used_directory.cache")
if os.path.exists(filedialog_cache_file):
    with open(filedialog_cache_file, "r") as f:
        last_used_dir = f.read()
else:
    last_used_dir = ""
if not os.path.exists(last_used_dir):
    last_used_dir = os.path.expanduser("~")

file_path = filedialog.askopenfilename(
    defaultextension=".sqlite3", 
    filetypes=[("SQLite3 database files", "*.sqlite3")],
    initialdir=last_used_dir,
)
if file_path == "":
    print("No file selected. Exiting.")
    exit()
DATABASE_FILE = os.path.normpath(file_path)
with open(filedialog_cache_file, "w") as f:
    f.write(os.path.dirname(DATABASE_FILE))
del root, filedialog_cache_file, last_used_dir, file_path




############
# CONSTANTS
############

# Each value stored in an SQLite database (or manipulated by the database engine) has one of the following storage classes:
#   NULL. The value is a NULL value.
#   INTEGER. The value is a signed integer, stored in 0, 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.
#   REAL. The value is a floating point value, stored as an 8-byte IEEE floating point number.
#   TEXT. The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).
#   BLOB. The value is a blob of data, stored exactly as it was input.


DATABSE_RECORD_LAYOUT_DATA_TYPES = {
    "demographics": {
        "ID_SUBJECT": "TEXT",
        "DT_BIRTH": "TEXT",
        "GENDER": "TEXT",
        "DT_DEATH": "TEXT",
        "CAUSE_DEATH_1": "TEXT",
        "CAUSE_DEATH_2": "TEXT",
        "DT_START_ASSIST": "TEXT",
        "DT_END_ASSIST": "TEXT",
        "CIVIL_STATUS": "TEXT",
        "JOB_COND": "TEXT",
        "EDU_LEVEL": "INTEGER"
    },
    "diagnoses": {
        "ID_SUBJECT": "TEXT",
        "DIAGNOSIS": "TEXT",
        "CODING_SYSTEM": "TEXT",
        "DATE_DIAG": "TEXT",
        "MAIN_DIAG": "TEXT",
        "DATE_DIAG_END": "TEXT",
        "SETTING": "TEXT",
        "DATE_ADMISSION": "TEXT",
        "DATE_DISCHARGE": "TEXT",
        "HOSPITAL_TYPE": "TEXT",
        "ADMISSION_TYPE": "TEXT"
    },
    "pharma": {
        "ID_SUBJECT": "TEXT",
        "DT_PRESCR": "TEXT",
        "ATC_CHAR": "TEXT",
        "QTA_NUM": "INTEGER",
        "DAYS": "INTEGER",
        "DAYS_TOT": "INTEGER"
    },
    "interventions": {
        "ID_SUBJECT": "TEXT",
        "DT_INT": "TEXT",
        "TYPE_INT": "TEXT",
        "STRUCTURE": "TEXT",
        "OPERATOR_1": "TEXT",
        "OPERATOR_2": "TEXT",
        "OPERATOR_3": "TEXT"
    },
    "physical_exams": {
        "ID_SUBJECT": "TEXT",
        "DT_INT": "TEXT",
        "TYPE_INT": "TEXT"
    }
}



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


##################
# DATABASE OBJECT
##################

DB = sqlite3.connect(DATABASE_FILE)


##############
# UTILITIES
##############

def get_tables(connection: sqlite3.Connection) -> list[str]:
    """ Get the names of the tables in the database.
    connection: sqlite3.Connection
        The connection to the database.
    Returns a list of strings, each string is the name of a table in the database.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [c[0] for c in cursor.fetchall()]
    cursor.close()
    tables.sort()
    return tables

def get_all_tables(connection: sqlite3.Connection) -> list[str]:
    main_tables = get_tables(connection)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_temp_master WHERE type='table'")
    temp_tables = [c[0] for c in cursor.fetchall()]
    cursor.close()
    temp_tables.sort()
    main_tables.extend(temp_tables)
    return main_tables

def get_temp_tables(connection: sqlite3.Connection) -> list[str]:
    """ Get the names of the temporary tables in the database.
    connection: sqlite3.Connection
        The connection to the database.
    Returns a list of strings, each string is the name of a temporary table in the database.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_temp_master WHERE type='table'")
    tables = [c[0] for c in cursor.fetchall()]
    cursor.close()
    tables.sort()
    return tables

def get_column_names(connection: sqlite3.Connection, table: str) -> list[str]:
    """ Get the names of the columns in a table of the database.
    connection: sqlite3.Connection
        The connection to the database.
    table: str
        The name of the table.
    Returns a list of strings, each string is the name of a column in the table.
    """
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [c[1] for c in cursor.fetchall()]
    cursor.close()
    return columns

def get_column_types(connection: sqlite3.Connection, table: str) -> list[str]:
    """ Get the types of the columns in a table of the database.
    connection: sqlite3.Connection
        The connection to the database.
    table: str
        The name of the table.
    Returns a list of strings, each string is the type of a column in the table.
    """
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [c[2] for c in cursor.fetchall()]
    cursor.close()
    return columns

def standardize_table_names(connection: sqlite3.Connection) -> None:
    """All table names should be lowercase, without spaces before or after,
    and no spaces in between words.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [c[0] for c in cursor.fetchall()]
    for table in tables:
        new_table = table.strip().lower().replace(" ", "_")
        if table != new_table:
            print(f"Renaming table '{table}' to '{new_table}'")
            cursor.execute(f"ALTER TABLE {table} RENAME TO {new_table}")
    cursor.close()

def check_database_has_tables(connection: sqlite3.Connection, cohorts_required:bool=False) -> tuple[bool, list[str]]:
    """ Check if the database has the necessary tables.
    connection: sqlite3.Connection
        The connection to the database.
    cohorts_required: bool
        If True, the 'cohorts' table is required.

    Returns a tuple with two elements:
    - bool: True if the database has the necessary tables, False otherwise.
    - list[str]: the list of tables that are missing in the database (if True, empty list).
    """
    # required tables
    required_tables = ["demographics", "diagnoses", "interventions", "pharma", "physical_exams"]
    if cohorts_required:
        required_tables.append("cohorts")
    # logic
    tables = get_tables(connection)
    missing_tables = [t for t in required_tables if t not in tables]
    return len(missing_tables) == 0, missing_tables

def hash_database_file(file_path: str) -> str:
    """ Compute the hash of the database file.
    file_path: str
        The path to the database file.
    Returns the hash of the file.
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(1048576), b""):
            md5.update(byte_block)
    return md5.hexdigest()

def get_original_database_hash_file_path() -> str:
    """ Get the path to the file that contains the hash of the original database file.
    Returns the path to the file.
    """
    fname = "db_hash_original.cache"
    path = os.path.normpath(
        os.path.join(get_cache_folder(), fname)
    )
    return path

def get_slim_database_hash_file_path() -> str:
    """ Get the path to the file that contains the hash of the slim database file.
    Returns the path to the file.
    """
    fname = "db_hash_slim.cache"
    path = os.path.normpath(
        os.path.join(get_cache_folder(), fname)
    )
    return path

def detect_original_database_has_changed() -> bool:
    """ Detect if the database file has changed since the last preprocessing.
    Returns True if the database file has changed, False otherwise.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        return True
    cache_file = get_original_database_hash_file_path()
    if not os.path.exists(cache_file):
        return True
    with open(cache_file, "r") as f:
        old_hash = f.read()
    database_file_hash = hash_database_file(DATABASE_FILE)
    return old_hash != database_file_hash

def get_slim_database_filepath() -> str:
    """ Get the path to the slim database file.
    Returns the path to the slim database file.
    """
    return os.path.normpath(
        os.path.join(
            os.path.dirname(DATABASE_FILE),
            f"{os.path.basename(DATABASE_FILE).replace('.sqlite3', '.jasqlite3')}"
        )
    )

def detect_slim_database_has_changed() -> bool:
    """ Detect if the slim database file has changed since the last preprocessing.
    Returns True if the slim database file has changed, False otherwise.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        return True
    cache_file = get_slim_database_hash_file_path()
    if not os.path.exists(cache_file):
        return True
    with open(cache_file, "r") as f:
        old_hash = f.read()
    slim_database_file = get_slim_database_filepath()
    if not os.path.exists(slim_database_file):
        return True
    slim_database_file_hash = hash_database_file(slim_database_file)
    return old_hash != slim_database_file_hash

def write_to_original_database_hash_file(hash_: str) -> None:
    """ Write the hash of the database file to a file in the cache folder.
    hash_: str
        The hash of the database file.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        os.makedirs(hash_folder)
    cache_file = get_original_database_hash_file_path()
    with open(cache_file, "w") as f:
        f.write(hash_)

def write_to_slim_database_hash_file(hash_: str) -> None:
    """ Write the hash of the slim database file to a file in the cache folder.
    hash_: str
        The hash of the slim database file.
    """
    hash_folder = get_cache_folder()
    if not os.path.exists(hash_folder):
        os.makedirs(hash_folder)
    cache_file = get_slim_database_hash_file_path()
    with open(cache_file, "w") as f:
        f.write(hash_)

def slim_down_database(connection: sqlite3.Connection) -> tuple[str, bool]:
    """To be run before the preprocessing of the database,
    to slim down the database and make it faster to process
    and discard useless data.

    A new database file is created named 'slim_<original_file_name>'.
    The process is applied only if it is the first time that the original database is accessed,
    if the original database has changed since the first time it was accessed,
    or if the slim database is not found or has changed since the last time it was created.
    To detect these changes, cached hashes of the original database file and the slim database file
    are stored in the cache folder and used as reference.

    Returns the file name of the slim database and a boolean indicating if the process was applied.
    The original database file, the one the user selects, is not modified in any way.
    """
    new_db_file = get_slim_database_filepath()
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # check if the process has to run
    print("Detecting changes in the databases...", end=" ")
    # conditions to not run the process (to exit this function):
    # - the slim database file does not exist
    condition_1 = os.path.exists(new_db_file)
    # - the original database file has changed
    condition_2 = not detect_original_database_has_changed()
    # - the slim database file has changed
    condition_3 = not detect_slim_database_has_changed()
    # - decide
    if condition_1 and condition_2 and condition_3:
        print("none found!")
        return new_db_file, False
    print("changes found! Processing...", end=" ")
    # apply the process
    cursor = connection.cursor()
    # save the hash of the original database file for next time
    write_to_original_database_hash_file(hash_database_file(DATABASE_FILE))
    # permanently delete the slim database file if it exists
    if os.path.exists(new_db_file):
        os.remove(new_db_file)
    # create the new slim database file
    cursor.execute(f"ATTACH DATABASE '{new_db_file}' AS slim")
    # slim down the pharma table
    cursor.execute("""
        CREATE TABLE slim.pharma AS
        SELECT *
        FROM pharma
        WHERE
            ATC_CHAR LIKE 'N06A%' /* Antidepressants */
            OR
            ATC_CHAR LIKE 'N05A%' /* Antipsycotics Agents (I and II generations) and Lithium (N05AN%) */
            OR
            ATC_CHAR = 'N03AX09' /* Lamotrigine */
            OR
            ATC_CHAR = 'N03AG01' /* Valproic acid */
            OR
            ATC_CHAR = 'N03AF01' /* Carbamazepine */
            /* Here, casting is not necessary because pattern-matching with LIKE also */
            /* works wether ATC_CHAR is BLOB or TEXT independently */
    """)
    # slim down the diagnoses table
    cursor.execute("""
        CREATE TABLE slim.diagnoses AS
        SELECT *
        FROM diagnoses
        WHERE
            (
                cast(CODING_SYSTEM AS TEXT) = 'ICD9'
                AND
                (
                    substr(cast(DIAGNOSIS AS TEXT),1,3) IN (
                                                '311', /* Depression */
                                                '295', '297', /* Schizophrenic Disorder */
                                                /* Bipolar Disorder */
                                                '301' /* Personality Disorder */
                                                /* Anxiety Disorders */
                                                /* Suicidal Behaviour */
                                            )
                    OR
                    substr(cast(DIAGNOSIS AS TEXT),1,4) IN (
                                                '2962', '2963', '2980', '3004', '3090', '3091', /* Depression */
                                                '2982', '2983', '2984', '2988', '2989', /* Schizophrenic Disorder */
                                                '2960', '2961', '2964', '2965', '2966', '2967', '2981', /* Bipolar Disorder */
                                                /* Personality Disorder */
                                                '3000', '3001', '3003', '3098', '3083', /* Anxiety Disorders */
                                                'E950', 'E951', 'E952', 'E953', 'E954', 'E955', 'E956', 'E957', 'E958', 'E959' /* Suicidal Behaviour */
                                            )
                    OR
                    substr(cast(DIAGNOSIS AS TEXT),1,5) IN (
                                                /* Depression */
                                                /* Schizophrenic Disorder */
                                                '29680', '29681', '29689', '29699', /* Bipolar Disorder */
                                                /* Personality Disorder */
                                                /* Anxiety Disorders */
                                                'V6284' /* Suicidal Behaviour */
                                            )
                )
            )
            OR
            (
                cast(CODING_SYSTEM AS TEXT) = 'ICD10'
                AND
                (
                   substr(cast(DIAGNOSIS AS TEXT),1,3) IN (
                                                'F32', 'F33', 'F39', /* Depression */
                                                'F20', 'F21', 'F22', 'F23', 'F24', 'F25', 'F28', 'F29', /* Schizophrenic Disorder */
                                                'F30', 'F31', /* Bipolar Disorder */
                                                'F60', 'F61', /* Personality Disorder */
                                                'F40', 'F41', 'F42', /* Anxiety Disorders */
                                                'X60', 'X61', 'X62', 'X63', 'X64', 'X65', 'X66', 'X67', 'X68', 'X69', 'X70', 'X71', 'X72', 'X73', 'X74', 'X75', 'X76', 'X77', 'X78', 'X79', 'X80', 'X81', 'X82', 'X83', 'X84', 'Y10', 'Y11', 'Y12', 'Y13', 'Y14', 'Y15', 'Y16', 'Y17', 'Y18', 'Y19', 'Y20', 'Y21', 'Y22', 'Y23', 'Y24', 'Y25', 'Y26', 'Y27', 'Y28', 'Y29', 'Y30', 'Y31', 'Y32', 'Y33', 'Y34' /* Suicidal Behaviour */
                                            )
                    OR
                    substr(cast(DIAGNOSIS AS TEXT),1,4) IN (
                                                'F341', 'F348', 'F349', 'F381', 'F388', 'F431', 'F432', /* Depression */
                                                /* Schizophrenic Disorder */
                                                'F340', 'F380', /* Bipolar Disorder */
                                                /* Personality Disorder */
                                                'F930', 'F931', 'F932', 'F430', 'F431', 'F438', 'F439' /* Anxiety Disorders */
                                                /* Suicidal Behaviour */
                                            )
                )
            )
    """)
    # tables 'interventions' is by construction already fine
    cursor.execute("CREATE TABLE slim.interventions AS SELECT * FROM interventions")
    # slim down the demographics table
    # to do so, find all the subjects that are in the slimmed down pharma and diagnoses tables
    # as well as in the interventions and physical_exams tables
    # create a unique set of subjects
    # then, create a new demographics table with only the subjects that appear in the unique set
    cursor.execute("""
        CREATE TABLE slim.demographics AS
        SELECT *
        FROM demographics
        WHERE ID_SUBJECT IN
        (
            SELECT DISTINCT ID_SUBJECT FROM slim.pharma
            UNION
            SELECT DISTINCT ID_SUBJECT FROM slim.diagnoses
            UNION
            SELECT DISTINCT ID_SUBJECT FROM slim.interventions
        )
    """)
    # slim down the physical_exams table from the unique set of subjects in the demographics table
    cursor.execute("""
        CREATE TABLE slim.physical_exams AS
        SELECT *
        FROM physical_exams
        WHERE ID_SUBJECT IN
        (
            SELECT DISTINCT ID_SUBJECT FROM slim.demographics
        )
    """)
    # commit changes and close
    connection.commit()
    cursor.close()
    # save the hash of the slim database file for next time
    write_to_slim_database_hash_file(hash_database_file(new_db_file))
    print("done!")
    return new_db_file, True


def preprocess_database_data_types(connection: sqlite3.Connection, force: bool=False) -> None:
    # Note: this function depends of the global variable DATABSE_RECORD_LAYOUT_DATA_TYPES
    #       From experiments it came out that the current configuration takes up
    #       much more space than the "original", unprocessed database.
    #       I think this might be due to the use of TEXT data types instead of BLOB
    #       which might be more efficient in storing short textual data.
    #       If changed to BLOB, it would be necessary to change all the comparisons
    #       in the code that use the data in the database.
    """ Perform preprocessing on all the tables of the ja dashboard database (the one that went throught the process of slimming down).
    Note: the input connection must be to the slimmed down database.
    The preprocessing consists of checking the data types of the columns.
    The preprocessing is done only if the original database file has changed since the last preprocessing
    or the slimmed down database file has changed since the last preprocessing, or if the force is True.
    The hash of the database file is saved in a file in the cache folder.
    Consider using force=True to force the preprocessing if the slim down process was applied.
    
    connection: sqlite3.Connection
        The connection to the ja_dashboard database.
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # logic
    cursor = connection.cursor()
    # first, check if the database was already preprocessed, in which case
    # we do not need to do anything unless the force is True
    # if force, just go on, else, check other conditions
    if not force:
        print("Detecting changes in the internal database, please wait...")
        # conditions to not apply this preprocessing (to exit this function):
        # - the original database file must not have changed since the last preprocessing
        condition_1 = not detect_original_database_has_changed()
        # - the slim database file must not have changed since the last preprocessing
        #   (this condition can be misleading as the hash file is saved after the slimming
        #    down process, that is why it is necessary to force execution if the slimming
        #    down process was applied)
        condition_2 = not detect_slim_database_has_changed()
        # - decide
        if condition_1 and condition_2:
            print("None found!")
            return
    print("Preprocessing internal database...")
    # get the tables names
    tables = get_tables(connection)
    # make sure that no column with the _new suffix exist in any table of the database
    for table in tables:
        column_names = get_column_names(connection, table)
        for cn in column_names:
            if cn.endswith("_new"):
                # remove the _new column
                query = f"""
                    ALTER TABLE {table}
                    DROP COLUMN {cn}
                """
                cursor.execute(query)
    # for each table, get the columns names and types
    tables = get_tables(connection)
    for table in tables:
        column_names = get_column_names(connection, table)
        column_types = get_column_types(connection, table)
        n_entries_ = cursor.execute(f"SELECT COUNT({column_names[0]}) FROM {table}").fetchone()[0]
        for cn, ct in zip(column_names, column_types):
            print(f"{table}: {cn} - {ct} ({n_entries_:,d} entries) -> {DATABSE_RECORD_LAYOUT_DATA_TYPES[table][cn]}")
            if table in DATABSE_RECORD_LAYOUT_DATA_TYPES and cn in DATABSE_RECORD_LAYOUT_DATA_TYPES[table]:
                print("\tupdating...", end="\r")
                # we need to copy the data in a new column with the correct type
                # and then drop the old column and rename the new column
                # create a new column with the correct type
                query = f"""
                    ALTER TABLE {table}
                    ADD COLUMN {cn}_new {DATABSE_RECORD_LAYOUT_DATA_TYPES[table][cn]}
                """
                cursor.execute(query)
                # copy the data from the old column to the new column
                query = f"""
                    UPDATE {table}
                    SET {cn}_new = CAST({cn} as {DATABSE_RECORD_LAYOUT_DATA_TYPES[table][cn]})
                """
                cursor.execute(query)
                # drop the old column
                query = f"""
                    ALTER TABLE {table}
                    DROP COLUMN {cn}
                """
                cursor.execute(query)
                # rename the new column
                query = f"""
                    ALTER TABLE {table}
                    RENAME COLUMN {cn}_new TO {cn}
                """ 
                cursor.execute(query)
    # be sure that no columns with the suffix _new exists
    tables = get_tables(connection)
    for table in tables:
        column_names = get_column_names(connection, table)
        for cn in column_names:
            if cn.endswith("_new"):
                # remove the _new column
                query = f"""
                    ALTER TABLE {table}
                    DROP COLUMN {cn}
                """
                cursor.execute(query)
    # commit changes and close
    connection.commit()
    cursor.close()
    # save the hash of the database file
    write_to_slim_database_hash_file(hash_database_file(get_slim_database_filepath()))
    print("Database preprocessed.")
    # done



#### incomplete
####  https://www.sqlitetutorial.net/sqlite-glob/

def add_cohorts_table(connection: sqlite3.Connection, force: bool=False) -> None:
    """ Create the temporary cohorts table in the database.

    Table columns:
    - ID_SUBJECT: alphanumeric (could be non-unique in the table)
    - YEAR_ENTRY: integer, the year considered for the inclusion in the cohort
    - AGE_ENTRY: integer, the age of the patient at the year of inclusion
    - ID_DISORDER: string, the disorder of the patient
    - ID_COHORT: string, the cohort of the patient
        - "SCHIZO", stands for Schizophrenic Disorder
        - "DEPRE", stands for Depression
        - "BIPOLAR", stands for Bipolar Disorder
    - ID_COHORT: string, the cohort of the patient
        - "A", stands for INCIDENT
        - "B", stands for PREVALENT
        - "C", stands for INCIDENT for age 18-25

    cohorts is kept into the jasqlite3 database as a table.
    Use force=True if any previous preprocessing has happened.
    This function will do its job only if the cohorts table is not found in the database
    or if force is True.

    connection: sqlite3.Connection
        The connection to the database.
        The database must have the following tables:
            demographics
            diagnoses
            interventions
            pharma
            physical_exams
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # check if the process has to run or not
    has_cohorts_table = "cohorts" in get_tables(connection)
    if has_cohorts_table and not force:
        print("The cohorts table is already in the database.")
        return
    print("Creating the cohorts table...", end=" ")
    # logic
    cursor = connection.cursor()
    WASHOUT_YEARS: int = 3
    # create the cohorts table
    cursor.execute("DROP TABLE IF EXISTS cohorts")
    cursor.execute("""
        CREATE TABLE cohorts (
            ID_SUBJECT TEXT,
            ID_DISORDER TEXT,
            YEAR_OF_ONSET INTEGER /* Not the year of the diagnosis, but the year of the first doubt which is afterward confirmed by a diagnosis */
        )
    """)
    # create the three temporary tables that are needed for there calculations
    def create_temp_tables(cursor: sqlite3.Cursor) -> None:
        # clear the temporary tables if they exist and recreate them
        cursor.execute("DROP TABLE IF EXISTS temp.t_pharma")
        cursor.execute("DROP TABLE IF EXISTS temp.t_diagnoses")
        cursor.execute("DROP TABLE IF EXISTS temp.t_interventions")
        cursor.execute("CREATE TEMP TABLE IF NOT EXISTS t_pharma (ID_SUBJECT TEXT, MIN_YEAR INTEGER)")
        cursor.execute("CREATE TEMP TABLE IF NOT EXISTS t_diagnoses (ID_SUBJECT TEXT, MIN_YEAR INTEGER)")
        cursor.execute("CREATE TEMP TABLE IF NOT EXISTS t_interventions (ID_SUBJECT TEXT, MIN_YEAR INTEGER)")
        cursor.execute("DELETE FROM t_pharma")
        cursor.execute("DELETE FROM t_diagnoses")
        cursor.execute("DELETE FROM t_interventions")
    # #######
    # SCHIZO
    # #######
    # - Get the year of first doubt of disorder for each subject.
    #   There has to be a diagnosis of the disorder in the diagnoses table.
    #   If, proior to the diagnosis (max 3 years), there is any pharma related to the disorder
    #   or any intervention (we do not look physical_exams), 
    #   the year of the first doubt is the year of the first.
    create_temp_tables(cursor)
    cursor.execute("""
        INSERT INTO t_diagnoses (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DATE_DIAG) AS INTEGER))
        FROM diagnoses
        WHERE
            CODING_SYSTEM IS NOT NULL
            AND
            DIAGNOSIS IS NOT NULL
            AND
            (
                (
                    CODING_SYSTEM = 'ICD9'
                    AND
                    (
                        substr(DIAGNOSIS,1,3) IN ('295', '297')
                        OR
                        substr(DIAGNOSIS,1,4) IN ('2980', '3004', '3090', '3091')
                        OR
                        substr(DIAGNOSIS,1,5) IN ('2962', '2963', '2964', '2965', '2966', '2967', '2981')
                    )
                )
                OR
                (
                    CODING_SYSTEM = 'ICD10'
                    AND
                    (   
                        substr(DIAGNOSIS,1,3) IN ('F20', 'F21', 'F22', 'F23', 'F24', 'F25', 'F28', 'F29')
                        OR
                        substr(DIAGNOSIS,1,4) IN ('F340', 'F380')
                    )
                )
            )
        GROUP BY ID_SUBJECT
    """)
    cursor.execute(f"""
        INSERT INTO t_pharma (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DT_PRESCR) AS INTEGER))
        FROM pharma
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses)
            AND
            ATC_CHAR IS NOT NULL AND ATC_CHAR LIKE 'N05A%' AND ATC_CHAR NOT LIKE 'N05AN%'
            AND
            pharma.DT_PRESCR IS NOT NULL
            AND
            CAST(strftime('%Y', pharma.DT_PRESCR) AS INTEGER) 
                BETWEEN
                    ( SELECT MIN_YEAR FROM t_diagnoses WHERE t_diagnoses.ID_SUBJECT = pharma.ID_SUBJECT ) - {WASHOUT_YEARS}
                    AND
                    ( SELECT MIN_YEAR FROM t_diagnoses WHERE t_diagnoses.ID_SUBJECT = pharma.ID_SUBJECT )
        GROUP BY ID_SUBJECT
    """)
    cursor.execute(f"""
        INSERT INTO t_interventions (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DT_INT) AS INTEGER))
        FROM interventions 
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses)
            AND
            interventions.DT_INT IS NOT NULL
            AND 
            CAST(strftime('%Y', interventions.DT_INT) AS INTEGER)
                BETWEEN
                    ( SELECT MIN_YEAR FROM t_diagnoses WHERE t_diagnoses.ID_SUBJECT = interventions.ID_SUBJECT ) - {WASHOUT_YEARS}
                    AND
                    ( SELECT MIN_YEAR FROM t_diagnoses WHERE t_diagnoses.ID_SUBJECT = interventions.ID_SUBJECT )
        GROUP BY ID_SUBJECT
    """)
    # Insert in cohorst all the subjects that have a diagnosis
    # As the year of onset, use the min date from the diagnosis if no previous record
    # of pharma and interventions is found in the previous 3 years inclusive.
    # If it is found, use the min of the previous records.
    cursor.execute("""
        INSERT INTO cohorts (ID_SUBJECT, ID_DISORDER, YEAR_OF_ONSET)
        SELECT 
            ID_SUBJECT, 
            'SCHIZO', 
            MIN_YEAR
        FROM t_diagnoses
        /* by selecting from this table, I know that the subject was diagnosed */
        /* I can use this to select the subjects that have a record of pharma or interventions */
        /* before the diagnosis but after the year of diagnosis - WASHOUT_YEARS */
    """)
    cursor.execute(f"""
        UPDATE cohorts
        SET YEAR_OF_ONSET = (
            /*
            If i'm setting, it means that one of the two conditions in the WHERE is true:
            So I can take the minimum of MIN_YEAR between the two tables that lies in the previous 3 years inclusive
            as the new YEAR_OF_ONSET.
            It is possible that the subjects in diagnosis have no record in pharma or interventions.
            */
            SELECT MIN(MIN_YEAR)
            FROM (
                SELECT YEAR_OF_ONSET AS MIN_YEAR FROM cohorts WHERE ID_SUBJECT = cohorts.ID_SUBJECT
                UNION
                SELECT MIN_YEAR FROM t_pharma WHERE ID_SUBJECT = cohorts.ID_SUBJECT
                UNION
                SELECT MIN_YEAR FROM t_interventions WHERE ID_SUBJECT = cohorts.ID_SUBJECT
            )
        )
        WHERE
            ID_DISORDER = 'SCHIZO'
            AND
            (
                ID_SUBJECT IN ( SELECT ID_SUBJECT FROM t_pharma )
                OR
                ID_SUBJECT IN ( SELECT ID_SUBJECT FROM t_interventions )     
            )
    """)
    return
    # DEPRE
    
    # BIPOLAR




    # delete the temporary tables
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS t_pharma")
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS t_diagnoses")
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS t_interventions")
    # commit changes and close
    connection.commit()
    cursor.close()
    # hash and save hash
    write_to_slim_database_hash_file(
        hash_database_file(
            get_slim_database_filepath()
        )
    )

















from ..indicator.widget import AGE_WIDGET_INTERVALS

def make_age_startification_tables(connection: sqlite3.Connection, year_of_inclusions_list: list[int]|None=None, age_stratifications: dict[str:tuple]|None=None, command: str="create"):
    """ Update the age stratification views to speed up the process of stratifying by age.
        Age of patients is computed with respect to the year of inclusion.
        The created temporary tables contain the ID_SUBJECT of the patients that are in the age range for the year of inclusion.
        The temporary tables are created if they do not exist, otherwise they are replaced.
        Temporary tables are used to speed up the process of stratifying by age, and will be automatically deleted
        when the connection is closed.

        Temporary tables do not appear in the SQLITE_SCHEMA table.
        Temporary tables and their indices and triggers occur in another special table named SQLITE_TEMP_SCHEMA. 
        SQLITE_TEMP_SCHEMA works just like SQLITE_SCHEMA except that it is only visible to the application that 
        created the temporary tables. To get a list of all tables, both permanent and temporary,
        one can use a command similar to the following:

        SELECT name FROM 
        (SELECT * FROM sqlite_schema UNION ALL SELECT * FROM sqlite_temp_schema)
        WHERE type='table'
        ORDER BY name

        Inputs:
        - connection: sqlite3.Connection
            The connection to the database.
            The database must have the following tables:
                demographics
                diagnoses
                interventions
                pharma
                physical_exams
        - year_of_inclusions_list: list[int]
            The list of years of inclusion for the cohorts.
        - age_stratifications: list[tuple[int, int]]
            A dict of str:tuple[int, int] where the key is the name of the table and the tuple is the age range.
            The new temporary views will be called "demographics_<yoi>_<str>", where <yoi> is the year of inclusion (int) and <str> is the key.
            Each tuple has the following structure:
            (min_age_included, max_age_included)
        - command: str
            The command to execute. Can be "create" or "drop".
            If "create", the temporary tables are created and overwritten if they exist.
            If "drop", the temporary tables are dropped if they exist and are not created anew.
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # check input
    if age_stratifications is None:
        print("\t*** - WARNING - ***\nFunction make_age_startification_tables: age_stratifications is None, using default values.")
        print("\tThis should be done only fo rdebugging purposes.")
        print("if this is production use, provide the age_stratifications parameter.")
        age_stratifications = {
            "All": (1,150),
            "18-": (1, 18),
            "18-65": (18, 65),
            "65+": (65, 150)
        }
    if year_of_inclusions_list is None:
        year_of_inclusions_list = [int(time.localtime().tm_year)]
    else:
        year_of_inclusions_list = [int(y) for y in year_of_inclusions_list]
        lcy_ = int(time.localtime().tm_year)
        for y in year_of_inclusions_list:
            if y > lcy_:
                raise ValueError(f"year_of_inclusions_list must be in the past, {y} is in the future.")
    if command not in ["create", "drop"]:
        raise ValueError("command must be 'create' or 'drop'")
    # logic
    cursor = connection.cursor()
    # drop the views if they exist (get all tables and views names, both permanent and temporary)
    all_tables = [a for a in cursor.execute(
        "SELECT name FROM sqlite_temp_schema").fetchall()
    ]
    for t in all_tables:
        if t[0].startswith("demographics_"):
            cursor.execute(f"DROP TABLE IF EXISTS '{t[0]}'")
    connection.commit()
    if command == "drop":
        cursor.close()
        return
    # create the tables:
    # for each patient in the demographics table, check if the patient is in the age range
    # for the different years of inclusion
    # naming convention example: demographics_2018_26_40
    i_ = 0
    for year_of_inclusion in year_of_inclusions_list:
        for age_name, age_tuple in age_stratifications.items():
            print(f"Creating temporary tables for age stratification... {100*i_/(len(year_of_inclusions_list)*len(age_stratifications)): 4.1f}%", end="\r")
            i_ += 1
            # create the table
            temp_view_name = f"demographics_{int(year_of_inclusion)}_{age_name}"
            query = f"""
                CREATE TEMPORARY TABLE '{temp_view_name}' AS
                    SELECT
                        DISTINCT ID_SUBJECT
                    FROM
                        demographics
                    WHERE 
                        ({year_of_inclusion} - CAST(strftime('%Y', DT_BIRTH) as INT) BETWEEN {age_tuple[0]} AND {age_tuple[1]})
                        AND
                        (
                            (CAST(strftime('%Y', DT_DEATH) as INT) > {year_of_inclusion})
                            OR
                            (DT_DEATH IS NULL)
                        )
            """
            cursor.execute(query)
    print(" "*70, end="\r")
    connection.commit()
    # close the cursor
    cursor.close()

def stratify_demographics(connection: sqlite3.Connection, **kwargs) -> str:
    """ Given the database with the tables of the available age ranges, stratify the patients according to the kwargs parameters.
    This function outputs a string, that is the name of the table that stores the IDs of the patients that satisfy the conditions.

    NOTE!!
    After you are done with the output table, remember to drop it with the following command:
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        connection.commit() 
    
    kwargs:
    - year_of_inclusion: int
        The year of inclusion of the patients in the cohort.
        If none provided, the current year. Must be present in the age-stratified demographics tables.
    - age: list[str]
        A list of age range identifiers, such as "14-", "25-45" or "65+".
        Must be compatible with the age-stratified demographics tables.
    - gender: str
        in ["A", "A-U", "M", "F", "U"]
    - civil status: str
        in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
    - job condition: str
        in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
    - educational level: str
        in ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]
    """
    # inputs
    year_of_inclusion = kwargs.get("year_of_inclusion", time.localtime().tm_year)
    year_of_inclusion = int(year_of_inclusion)
    age_intervals_list = kwargs.get("age", None)
    if age_intervals_list is None:
        raise ValueError(f"age must be provided and must be a list of strings choosing from {AGE_WIDGET_INTERVALS.keys()}. Found {age_intervals_list}")
    if not isinstance(age_intervals_list, list):
        raise ValueError(f"age must be a list of strings choosing from {AGE_WIDGET_INTERVALS.keys()}. Found {age_intervals_list} (not a list)")
    if len(age_intervals_list) == 0:
        raise ValueError(f"age must be a non-empty list of strings choosing from {AGE_WIDGET_INTERVALS.keys()}. Found {age_intervals_list}")
    for age_interval in age_intervals_list:
        if age_interval not in AGE_WIDGET_INTERVALS.keys():
            raise ValueError(f"age must be a list of strings choosing from {AGE_WIDGET_INTERVALS.keys()}. Found {age_interval}")
    _available_genders = ["A", "A-U", "M", "F", "U"]
    gender = kwargs.get("gender", None)
    if gender is None:
        raise ValueError("gender must be provided")
    if gender not in _available_genders:
        raise ValueError(f"gender must be in {_available_genders}")
    _available_civil_status = ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
    civil_status = kwargs.get("civil_status", None)
    if civil_status is None:
        raise ValueError("civil_status must be provided")
    if civil_status not in _available_civil_status:
        raise ValueError(f"civil_status must be in {_available_civil_status}")
    _available_job_conditions = ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
    job_condition = kwargs.get("job_condition", None)
    if job_condition is None:
        raise ValueError("job_condition must be provided")
    if job_condition not in _available_job_conditions:
        raise ValueError(f"job_condition must be in {_available_job_conditions}")
    _available_educational_levels = ["All", "All-Unknown", "0-5", "6-8", "9-13", ">=14", "Unknown"]
    educational_level = kwargs.get("educational_level", None)
    if educational_level is None:
        raise ValueError("educational_level must be provided")
    if educational_level not in _available_educational_levels:
        raise ValueError(f"educational_level must be in {_available_educational_levels}")
    # logic
    cursor = connection.cursor()
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection, cohorts_required=False)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # create the table of stratified patients ids
    time_string = datetime.datetime.now().strftime("%H%M%S%f")
    table_name = "stratified_patients_" + time_string
    queries = []
    # QUERY 1: drop the table if it exists
    queries.append(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    # QUERY 2: Create a subtable of the whole demographics table (all columns)
    #          where only the patients with IDS in the age-stratified
    #          tables are allowed
    #          This table is to be dropped before committing the changes
    temp_table_name = "temp_table_" + time_string
    query = f"""
        CREATE TEMPORARY VIEW {temp_table_name} AS
            SELECT * FROM demographics
            WHERE ID_SUBJECT IN ("""
    for i, age_interval in enumerate(age_intervals_list):
        query += f"SELECT ID_SUBJECT FROM 'demographics_{year_of_inclusion}_{age_interval}'"
        if i < len(age_intervals_list) - 1:
            query += " UNION "
    query += ")"
    queries.append(query)
    # QUERY 3: Create the final table with the stratified patients ids
    #          according to the other parameters looking just at the
    #          patients in the temp_table
    if gender == "A":
        gender_selector_statement = "1"
    elif gender == "A-U":
        gender_selector_statement = f"(GENDER IS NOT NULL)"
    elif gender == "U":
        gender_selector_statement = f"(GENDER IS NULL)"
    else:
        gender_selector_statement = f"(GENDER = '{gender}')"
    if civil_status == "All":
        civil_status_selector_statement = "1"
    elif civil_status == "All-Other":
        civil_status_selector_statement = f"(CIVIL_STATUS != 'Other' AND CIVIL_STATUS IS NOT NULL)"
    else:
        civil_status_selector_statement = f"(CIVIL_STATUS = '{civil_status}')"
    if job_condition == "All":
        job_condition_selector_statement = "1"
    elif job_condition == "All-Unknown":
        job_condition_selector_statement = f"(JOB_COND IS NOT NULL)"
    elif job_condition == "Unknown":
        job_condition_selector_statement = f"(JOB_COND IS NULL)"
    else:
        job_condition_selector_statement = f"(JOB_COND = '{job_condition}')"
    if educational_level == "All":
        educational_level_selector_statement = "1"
    elif educational_level == "All-Unknown":
        educational_level_selector_statement = f"(EDU_LEVEL IS NOT NULL)"
    elif educational_level == "Unknown":
        educational_level_selector_statement = f"(EDU_LEVEL IS NULL)"
    else:
        educational_level_selector_statement = f"(EDU_LEVEL = '{educational_level}')"
    query = f"""
            CREATE TEMPORARY TABLE {table_name} AS
                SELECT 
                    DISTINCT ID_SUBJECT FROM {temp_table_name}
                WHERE
                    (
                    {gender_selector_statement}
                    AND
                    {civil_status_selector_statement}
                    AND
                    {job_condition_selector_statement}
                    AND
                    {educational_level_selector_statement}
                    )
    """
    queries.append(query)
    # QUERY 4: drop the temporary table temp_table
    queries.append(f"DROP VIEW IF EXISTS {temp_table_name};")
    # execute the queries
    for q in queries:
        cursor.execute(q)
    connection.commit()
    # RECAP:
    # - first, the table is dropped if it exists
    # - then, a temporary table is created with the patients that are in the age-stratified tables
    # - finally, the final table is created with the patients that satisfy the other conditions
    # - table_name contains the IDs of the patients that satisfy the conditions
    #   under the column named "ID_SUBJECT"
    # close the cursor
    cursor.close()
    # return the table name
    return table_name


# other utilities

def get_tables_dimensions(connection: sqlite3.Connection) -> dict[str:int]:
    cursor = connection.cursor()
    tables = get_tables(connection)
    tables_dimensions = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        tables_dimensions[table] = cursor.fetchone()[0]
    cursor.close()
    return tables_dimensions

def print_tables_dimensions(connection: sqlite3.Connection):
    tables_dimensions = get_tables_dimensions(connection)
    for table, dim in tables_dimensions.items():
        print(f"Table {table} has {dim:,d} rows")






#########################################
# DATABASE PREPARATION FOR THE DASHBOARD
#########################################

# Standardize tables names
standardize_table_names(DB)

# Check if the database has the necessary tables
is_ok, missing = check_database_has_tables(DB)
if not is_ok:
    raise ValueError("The database is missing the following tables which are required:", missing)
#
#
#
#
#
#
#
print("DEBUG *************   LINE 1660")
db2_ = sqlite3.connect(get_slim_database_filepath())
cursor = db2_.cursor()
print("Tables *** : ", get_tables(db2_))
cursor.execute("DROP TABLE IF EXISTS cohorts")
print("Tables *** : ", get_tables(db2_))
cursor.close()
write_to_slim_database_hash_file(hash_=hash_database_file(get_slim_database_filepath()))
db2_.close()
#
#
#
#
#
#
#
#
#

# Preprocess the database: create a second database file (that will be used for the dashboard)
#                          containing only patients
#                          that are mental health patients of some sort, to exclude
#                          every other medical condition not of interest of the dashboard
new_db_path, has_been_slimmed = slim_down_database(DB)
DB.close()
DB = sqlite3.connect(new_db_path)

# Preprocess the ja database: fix data types
preprocess_database_data_types(DB, force=has_been_slimmed)

# Create the Cohorts table
add_cohorts_table(DB, force=True)

###
###
###
columns = get_column_names(DB, "cohorts")
print(columns)
cursor = DB.cursor()
cursor.execute("SELECT * FROM cohorts LIMIT 10;")
res = cursor.fetchall()
for r in res:
    for e in r:
        print(e, end="\t")
    print()
print("Number of rows in the cohorts table:",
    cursor.execute("SELECT COUNT(*) FROM cohorts;").fetchone()[0]
)
print("Min SCHIZO year of onset:",
    cursor.execute("SELECT MIN(YEAR_OF_ONSET) FROM cohorts WHERE ID_DISORDER = 'SCHIZO';").fetchone()[0]
)
print("Max SCHIZO year of onset:",
    cursor.execute("SELECT MAX(YEAR_OF_ONSET) FROM cohorts WHERE ID_DISORDER = 'SCHIZO';").fetchone()[0]
)
DB.close()

print("Database is ready!")
quit()



###
# Create the stratified demographics table
from ..indicator.widget import AGE_WIDGET_INTERVALS
from ..database.database import make_age_startification_tables
years_of_inclusion = [2018, 2019, 2020, 2021] ########################### to do after having cohorts, and use function get_years_of_inclusion
make_age_startification_tables(DB, AGE_WIDGET_INTERVALS)


# AGE STRAT TABLES? MAKE EM TEMPORARY










if __name__ == "__main__":
    # test database: read the database table names
    # and print the first 10 rows of each table
    # with column names
    cursor = DB.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [a[0] for a in cursor.fetchall()]
    for table in tables:
        print(f"Table: {table}")
        columns = cursor.execute(f"PRAGMA table_info({table});").fetchall()
        for c in columns:
            print(c[1], end="\t")
        print()
        for c in columns:
            print(c[2], end="\t")
        print()
        rows = cursor.execute(f"SELECT * FROM {table} LIMIT 10;").fetchall()
        for r in rows:
            for e in r:
                print(e, end="\t")
            print()
        