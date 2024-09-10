import os, time, datetime
import hashlib
import bokeh.palettes
import sqlite3

from ..caching.database import (
    hash_database_file,
    get_original_database_file_path,
    write_to_original_database_hash_file,
    get_slim_database_filepath,
    write_to_slim_database_hash_file,
    detect_original_database_has_changed,
    detect_slim_database_has_changed,
    
)

# This file contains all the functions to load, preprocess
# and work with the database
# The actual loading of the database is performed in the
# load_database.py file, so that it can be imported
# only ince in the dispatcher.py file,
# while this file can be imported as many times as needed.

#############
# CONSTANTS
#############

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
    "_bipolar_disorder_": "BIPO",
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

####################
# GENERIC UTILITIES
# - DATABASE
####################

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

def get_all_tables(connection: sqlite3.Connection) -> list[str]:
    main_tables = get_tables(connection)
    temp_tables = get_temp_tables(connection)
    main_tables.extend(temp_tables)
    return main_tables

def get_table_num_rows(connection: sqlite3.Connection, table: str) -> int:
    """ Get the number of rows in a table of the database.
    connection: sqlite3.Connection
        The connection to the database.
    table: str
        The name of the table.
    Returns the number of rows in the table.
    """
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    num_rows = int(cursor.fetchone()[0])
    cursor.close()
    return num_rows

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

def check_database_has_tables(connection: sqlite3.Connection, cohorts_required:bool=False, age_stratification_required: bool=False) -> tuple[bool, list[str]]:
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
    if age_stratification_required:
        required_tables.append("age_stratification")
    # logic
    tables = get_tables(connection)
    missing_tables = [t for t in required_tables if t not in tables]
    return len(missing_tables) == 0, missing_tables

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



##########################
# PREPROCESSING UTILITIES
##########################

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
    if condition_1:
        s_ = "ja database not found"
    elif not condition_2 and not condition_3:
        s_ = "both databases changed"
    elif not condition_2:
        s_ = "original database changed"
    elif not condition_3:
        s_ = "ja database changed"
    print(f"changes found! ({s_}) Processing...", end=" ")
    # apply the process
    cursor = connection.cursor()
    # save the hash of the original database file for next time
    write_to_original_database_hash_file(hash_database_file(get_original_database_file_path()))
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
        WHERE ID_SUBJECT IN (
            /* I want to keep every subject that has something
               either in the pharma, diagnoses, interventions tables 
            */
            SELECT ID_SUBJECT FROM slim.pharma
            UNION
            SELECT ID_SUBJECT FROM slim.diagnoses
            UNION
            SELECT ID_SUBJECT FROM slim.interventions
        )
    """)
    # slim down the physical_exams table from the unique set of subjects in the demographics table
    cursor.execute("""
        CREATE TABLE slim.physical_exams AS
        SELECT *
        FROM physical_exams
        WHERE ID_SUBJECT IN (
            SELECT ID_SUBJECT FROM slim.demographics
        )
    """)
    # commit changes and close
    connection.commit()
    cursor.close()
    # save the hash of the slim database file for next time
    write_to_slim_database_hash_file(hash_database_file(new_db_file))
    print("done!")
    return new_db_file, True

def create_indices_on_ja_database(connection: sqlite3.Connection, force=False) -> None:
    """ Create indices on the tables of the ja dashboard database.
    Runs only if force is True.
    """
    if not force:
        return
    cursor = connection.cursor()
    cursor.execute("CREATE INDEX idx_demographics_id_subject ON demographics(ID_SUBJECT)")
    cursor.execute("CREATE INDEX idx_diagnoses_id_subject ON diagnoses(ID_SUBJECT)")
    cursor.execute("CREATE INDEX idx_interventions_id_subject ON interventions(ID_SUBJECT)")
    cursor.execute("CREATE INDEX idx_pharma_id_subject ON pharma(ID_SUBJECT)")
    cursor.execute("CREATE INDEX idx_physical_exams_id_subject ON physical_exams(ID_SUBJECT)")
    # done
    connection.commit()
    cursor.close()
    write_to_slim_database_hash_file(hash_database_file(get_slim_database_filepath()))

def preprocess_database_data_types(connection: sqlite3.Connection, force: bool=False) -> None:
    _dbg = False
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
        print("Detecting changes in the internal database, please wait...", end=" ")
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
    print("Fixing internal database data types...")
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
        for cn, ct in zip(column_names, column_types):
            if _dbg:
                n_entries_ = get_table_num_rows(connection, table)
                print(f"{table}: {cn} - {ct} ({n_entries_:,d} entries) -> {DATABSE_RECORD_LAYOUT_DATA_TYPES[table][cn]}")
            if table in DATABSE_RECORD_LAYOUT_DATA_TYPES and cn in DATABSE_RECORD_LAYOUT_DATA_TYPES[table]:
                if _dbg:
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

def preprocess_database_datetimes(connection: sqlite3.Connection, force: bool=False) -> None:
    """ Perform preprocessing on all the datetime columns of the ja dashboard database.
    
    This runs only if force is True.
    """
    if not force:
        return
    print("Preprocessing date-time columns of the internal database...", end=" ")
    DATETIME_COLUMNS_REQUIRED = {
        "demographics": ["DT_BIRTH"],
        "diagnoses": ["DATE_DIAG"],
        "interventions": ["DT_INT"],
        "pharma": ["DT_PRESCR"],
        "physical_exams": ["DT_INT"]
    }
    DATETIME_COLUMNS_NOT_REQUIRED = {
        "demographics": ["DT_DEATH", "DT_START_ASSIST", "DT_END_ASSIST"],
        "diagnoses": ["DATE_DIAG_END", "DATE_ADMISSION", "DATE_DISCHARGE"],
        "interventions": [],
        "pharma": [],
        "physical_exams": []
    }
    pairs = [(k, v, True) for k, v in DATETIME_COLUMNS_REQUIRED.items()]
    pairs.extend([(k, v, False) for k, v in DATETIME_COLUMNS_NOT_REQUIRED.items()])
    cursor = connection.cursor()
    for table, columns, required in pairs:
        for column in columns:
            # first, drop rows that are not compliant with either:
            # - ISO 8601 format: 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
            # - YYMMDD10 format: 'YYYY/MM/DD'
            # - wrong YYMMDD10 formats: 'DD/MM/YYYY' or 'YYMMDD' or 'YYMMDD10'
            cursor.execute(f"""
                UPDATE {table}
                SET {column} = (
                    CASE
                        /* Shorten datetime to date */
                        WHEN ({column} GLOB '????-??-??*' AND LENGTH({column} > 10)) THEN substr({column},1,10)
                        /* Convert correct YYMMDD10 to ISO 8601 */
                        WHEN {column} GLOB '????/??/??*' THEN substr({column},1,4) ||'-'|| substr({column},6,2) ||'-'|| substr({column},9,2)
                        /* Convert wrong YYMMDD10 to ISO 8601 */
                        WHEN {column} GLOB '??/??/????*' THEN substr({column},7,4) ||'-'|| substr({column},4,2) ||'-'|| substr({column},1,2)
                        /* Convert YYYYMMDD to ISO 8601 (or DDMMYYYY but it will get it wrong) */
                        WHEN {column} GLOB '????????*' THEN substr({column},1,4) ||'-'|| substr({column},5,2) ||'-'|| substr({column},7,2)
                        /* 'YYMMDD' or 'YYMMDD10' cannot be addressed: how do you know if 19YY or 20YY? */
                        ELSE NULL
                    END
                )
            """)
            # remove rows with NULL values in column
            if required:
                cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE {column} IS NULL
                """)
    # commit changes and close
    connection.commit()
    cursor.close()
    # save the hash of the database file
    write_to_slim_database_hash_file(hash_database_file(get_slim_database_filepath()))
    print("done!")

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
    # Print out an estimation of the time it will take to process the data
    n_diagnoses = get_table_num_rows(connection, "diagnoses")
    entries_per_second_diagnoses = 111500.0
    n_pharma = get_table_num_rows(connection, "pharma")
    entries_per_second_pharma = 29500.0
    n_interventions = get_table_num_rows(connection, "interventions")
    entries_per_second_interventions = 7600.0
    overhead_seconds = 10.0
    tot_seconds = n_diagnoses/entries_per_second_diagnoses + n_pharma/entries_per_second_pharma + n_interventions/entries_per_second_interventions + overhead_seconds
    tot_seconds *= 3 # three mental disorders considered
    hours, minutes, seconds = tot_seconds//3600, (tot_seconds//60)%60, tot_seconds%60
    print(f"Estimated time: {hours:.0f}h {minutes:.0f}m {seconds:.0f}s")
    t0_ = time.time()
    # #######
    # SCHIZO
    # #######
    create_temp_tables(cursor)
    cursor.execute("""
        INSERT INTO t_diagnoses (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DATE_DIAG) AS INTEGER))
        FROM diagnoses
        WHERE
            (
                (
                    CODING_SYSTEM = 'ICD9'
                    AND
                    (
                        substr(DIAGNOSIS,1,3) IN ('295', '297')
                        OR
                        substr(DIAGNOSIS,1,4) IN ('2982', '2983', '2984', '2988', '2989')
                    )
                )
                OR
                (
                    CODING_SYSTEM = 'ICD10'
                    AND
                    (   
                        substr(DIAGNOSIS,1,3) IN ('F20', 'F21', 'F22', 'F23', 'F24', 'F25', 'F28', 'F29')
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
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            AND
            ATC_CHAR LIKE 'N05A%' AND ATC_CHAR NOT LIKE 'N05AN%'
            AND
            CAST(strftime('%Y', DT_PRESCR) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = pharma.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
    cursor.execute(f"""
        INSERT INTO t_interventions (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DT_INT) AS INTEGER))
        FROM interventions
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            AND
            CAST(strftime('%Y', DT_INT) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = interventions.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
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
                SELECT MIN_YEAR FROM (SELECT YEAR_OF_ONSET AS MIN_YEAR FROM cohorts WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_pharma WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_interventions WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
            )
        )
        WHERE
            ID_DISORDER = 'SCHIZO'
            AND
            ID_SUBJECT IN (
                SELECT ID_SUBJECT FROM t_pharma
                UNION
                SELECT ID_SUBJECT FROM t_interventions
                )
    """)
    ########
    # DEPRE
    ########
    create_temp_tables(cursor)
    cursor.execute("""
        INSERT INTO t_diagnoses (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DATE_DIAG) AS INTEGER))
        FROM diagnoses
        WHERE
            (
                (
                    CODING_SYSTEM = 'ICD9'
                    AND
                    (
                        substr(DIAGNOSIS,1,3) IN ('311')
                        OR
                        substr(DIAGNOSIS,1,4) IN ('2962', '2963', '2980', '3004', '3090', '3091')
                    )
                )
                OR
                (
                    CODING_SYSTEM = 'ICD10'
                    AND
                    (   
                        substr(DIAGNOSIS,1,3) IN ('F32', 'F33', 'F39')
                        OR
                        substr(DIAGNOSIS,1,4) IN ('F341', 'F348', 'F349', 'F381', 'F388', 'F431', 'F432')
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
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            AND
            ATC_CHAR LIKE 'N06A%'
            AND
            CAST(strftime('%Y', DT_PRESCR) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = pharma.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
    cursor.execute(f"""
        INSERT INTO t_interventions (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DT_INT) AS INTEGER))
        FROM interventions
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            AND
            CAST(strftime('%Y', DT_INT) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = interventions.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
    cursor.execute("""
        INSERT INTO cohorts (ID_SUBJECT, ID_DISORDER, YEAR_OF_ONSET)
        SELECT 
            ID_SUBJECT, 
            'DEPRE', 
            MIN_YEAR
        FROM t_diagnoses
    """)
    cursor.execute(f"""
        UPDATE cohorts
        SET YEAR_OF_ONSET = (
            SELECT MIN(MIN_YEAR)
            FROM (
                SELECT MIN_YEAR FROM (SELECT YEAR_OF_ONSET AS MIN_YEAR FROM cohorts WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_pharma WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_interventions WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
            )
        )
        WHERE
            ID_DISORDER = 'DEPRE'
            AND
            ID_SUBJECT IN (
                SELECT ID_SUBJECT FROM t_pharma
                UNION
                SELECT ID_SUBJECT FROM t_interventions
                )
    """)
    # BIPOLAR
    create_temp_tables(cursor)
    cursor.execute("""
        INSERT INTO t_diagnoses (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DATE_DIAG) AS INTEGER))
        FROM diagnoses
        WHERE
            (
                (
                    CODING_SYSTEM = 'ICD9'
                    AND
                    (
                        substr(DIAGNOSIS,1,4) IN ('2960', '2961', '2964', '2965', '2966', '2967', '2981')
                        OR
                        substr(DIAGNOSIS,1,5) IN ('29680', '29681', '29689', '29699')
                    )
                )
                OR
                (
                    CODING_SYSTEM = 'ICD10'
                    AND
                    (   
                        substr(DIAGNOSIS,1,3) IN ('F30', 'F31')
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
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            /*Bipolar has no contraints on the pharma, except it must be a mental health related pharma */
            /* Since pahrma is already filtered for mental health, no need to filter further */
            AND
            CAST(strftime('%Y', DT_PRESCR) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = pharma.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
    cursor.execute(f"""
        INSERT INTO t_interventions (ID_SUBJECT, MIN_YEAR)
        SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DT_INT) AS INTEGER))
        FROM interventions
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM t_diagnoses) /* for some reason, way faster than using INNER JOIN */
            AND
            CAST(strftime('%Y', DT_INT) AS INTEGER) - ( SELECT MIN_YEAR FROM t_diagnoses WHERE ID_SUBJECT = interventions.ID_SUBJECT LIMIT 1)
                BETWEEN -{WASHOUT_YEARS} AND 0
        GROUP BY ID_SUBJECT
    """)
    cursor.execute("""
        INSERT INTO cohorts (ID_SUBJECT, ID_DISORDER, YEAR_OF_ONSET)
        SELECT 
            ID_SUBJECT, 
            'BIPO', 
            MIN_YEAR
        FROM t_diagnoses
    """)
    cursor.execute(f"""
        UPDATE cohorts
        SET YEAR_OF_ONSET = (
            SELECT MIN(MIN_YEAR)
            FROM (
                SELECT MIN_YEAR FROM (SELECT YEAR_OF_ONSET AS MIN_YEAR FROM cohorts WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_pharma WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
                UNION
                SELECT MIN_YEAR FROM (SELECT MIN_YEAR FROM t_interventions WHERE ID_SUBJECT = cohorts.ID_SUBJECT LIMIT 1)
            )
        )
        WHERE
            ID_DISORDER = 'BIPO'
            AND
            ID_SUBJECT IN (
                SELECT ID_SUBJECT FROM t_pharma
                UNION
                SELECT ID_SUBJECT FROM t_interventions
                )
    """)
    # delete the temporary tables
    cursor.execute("DROP TABLE IF EXISTS temp.t_pharma")
    cursor.execute("DROP TABLE IF EXISTS temp.t_diagnoses")
    cursor.execute("DROP TABLE IF EXISTS temp.t_interventions")
    # This table will be queried a lot since it will be used for stratification (read only from here on)
    # so we need to create an index on ID_SUBJECT, ID_DISORDER, YEAR_OF_ONSET to speed up the process
    cursor.execute("CREATE INDEX idx_cohorts ON cohorts (ID_SUBJECT, ID_DISORDER, YEAR_OF_ONSET)")
    # commit changes and close
    connection.commit()
    cursor.close()
    # hash and save hash
    write_to_slim_database_hash_file(
        hash_database_file(
            get_slim_database_filepath()
        )
    )
    t1_ = time.time()
    h_ = int((t1_ - t0_)//3600)
    m_ = int((t1_ - t0_)//60 - h_*60)
    s_ = int((t1_ - t0_)%60)
    print(f"done! (took {h_}h {m_}m {s_}s)")

def get_all_years_of_inclusion(connection: sqlite3.Connection) -> list[int]:
    m, l = check_database_has_tables(connection, cohorts_required=True)
    if not m:
        raise ValueError("The database is missing the following tables: ", l)
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(DISTINCT YEAR_OF_ONSET) FROM cohorts;")
    y_min = cursor.fetchone()[0]
    y_now = int(time.localtime().tm_year)
    years_of_inclusion = [y for y in range(y_min, y_now+1)] # range is inclusive
    cursor.close()
    return years_of_inclusion

def get_age_stratification_column(year_of_inclusion: int, ages: tuple[int, int]) -> str:
    """ Return the name of the column in the age stratification table.
    The column name is constructed as follows:
    ast_<year_of_inclusion_yyyy>_<age_start>_<age_end>, for example 'ast_2010_18_65'.
    
    Input ages must be a tuple of two integers, the first one being the start of the age interval
    and the second one being the end of the age interval.
    """
    return f"ast_{year_of_inclusion}_{ages[0]}_{ages[1]}"

def get_age_stratification_column_all(year_of_inclusion_list: list[int], age_intervals: list[tuple[int, int]]) -> list[str]:
    """ Return a list of all the column names for the age stratification table.
    The column names are constructed as follows:
    ast_<year_of_inclusion_yyyy>_<age_start>_<age_end>, for example 'ast_2010_18_65'.
    
    Input ages must be a tuple of two integers, the first one being the start of the age interval
    and the second one being the end of the age interval.
    """
    return [get_age_stratification_column(yoi, ai) for yoi in year_of_inclusion_list for ai in age_intervals] + [f"incident_18_25_{yoi}" for yoi in year_of_inclusion_list]

def make_age_startification_tables(connection: sqlite3.Connection, year_of_inclusions_list: list[int]|None=None, age_stratifications: dict[str:tuple]|None=None, force: bool=True):
    """ Age of all patients in demographics is computed with respect to each year of inclusion.
        By convention, the age is computed as the difference between the year of inclusion and the year of birth,
        not accounting for the month and day of birth.

        The created tables are stored permanentrly in the ja database in table 'age_stratification'.
        The process runs only if force is True, which means that the tables are created anew.
        Each table has num_unique_ID_SUBJECT_in_demographics rows and num_age_intervals columns,
        and columns are named following the convention 'ast_<year_of_inclusion_yyyy>_<age_start>_<age_end>'.
        Both age_start and age_end are inclusive.
        Each column is of type TEXT and holds either ID_SUBJECT data or NULL.

        This function additionally creates len(year_of_inclusions_list) tables for subjects located in the 18-25 years old inclusive
        to make stratification faster at runtime when the incident_18_25 cohort is concerned.
        These are named: incident_18_25_"+str(yoi).

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
            A list of tuples that define the age stratification intervals.
            Each tuple has the following structure:
            (min_age_included, max_age_included)
        - force: bool
            If True, the process will run even if the table already exist.
    """
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection, cohorts_required=True)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # check input
    if age_stratifications is None:
        print("\t*** - WARNING - ***\nFunction make_age_startification_tables: age_stratifications is None, using default values.")
        age_stratifications = [
            (1,150),
            (1, 18),
            (18, 65),
            (65, 150)
        ]
    if year_of_inclusions_list is None:
        print("\t*** - WARNING - ***\nFunction make_age_startification_tables: year_of_inclusions_list is None, using default values.")
        year_of_inclusions_list = get_all_years_of_inclusion(connection)
    else:
        year_of_inclusions_list = [int(y) for y in year_of_inclusions_list]
        lcy_ = int(time.localtime().tm_year)
        for y in year_of_inclusions_list:
            if y > lcy_:
                raise ValueError(f"year_of_inclusions_list must be in the past, {y} is in the future.")
    tables = get_all_tables(connection)
    if not force:
        if "age_stratification" in tables:
            return
    print("Creating age stratification tables...", end=" ")
    # logic
    cursor = connection.cursor()
    # each columns in the table is filled with the ID_SUBJECT of the patients that satisfy the conditions
    # since the number of rows is the same for all columns, if a column has less rows than the others, it
    # will be filled with null values.
    table_columns = get_age_stratification_column_all(year_of_inclusions_list, age_stratifications)
    table_num_rows = int(cursor.execute("SELECT COUNT(DISTINCT ID_SUBJECT) FROM demographics").fetchone()[0])
    # create the new table (discard old one if it exists)
    cursor.execute("DROP TABLE IF EXISTS age_stratification")
    table_creation_string = ", ".join([f"{col} TEXT DEFAULT NULL" for col in table_columns])
    cursor.execute(f"CREATE TABLE age_stratification ({table_creation_string})")
    # fill the tables
    # first fill table with NULL values for as many rows as there are in demographics' DISTINCT ID_SUBJECT
    for _ in range(table_num_rows):
        cursor.execute(f"""INSERT INTO age_stratification DEFAULT VALUES""")
    # to update the table, we need a temporary table where to store the unique, sorted ID_SUBJECT
    cursor.execute("CREATE TEMP TABLE buffer(ID_SUBJECT TEXT)")
    for yoi in year_of_inclusions_list:
        for ys, ye in age_stratifications:
            column_name = get_age_stratification_column(yoi, (ys, ye))
            # fill the temp table with the ID_SUBJECT of patients that satisfy the conditions
            cursor.execute("DELETE FROM buffer")
            cursor.execute(f"""
                INSERT INTO buffer
                SELECT DISTINCT ID_SUBJECT
                FROM demographics
                WHERE
                    (
                        /* at the year of inclusion, the patient must be alive (birth < yoi, death > yoi or null)*/
                        /* at the year of inclusion, the patient must fall into the inclusive age range */
                        ({yoi} - CAST(strftime('%Y', DT_BIRTH) as INT) BETWEEN {ys} AND {ye})
                        AND
                        (
                            (CAST(strftime('%Y', DT_DEATH) as INT) > {yoi})
                            OR
                            (DT_DEATH IS NULL)
                        )
                        /* Also, since I will work only with the subjects that appear in COHORTS, I can filter out the rest 
                           When cohorts will consider every possible mental disorter, this condition will no nothing.
                           Else, it will filter out the subjects that do not have a record in the cohort table.
                        */
                        AND
                        ID_SUBJECT IN (SELECT DISTINCT ID_SUBJECT FROM cohorts)
                    )
                ORDER BY ID_SUBJECT
            """)
            # update the age_stratification table
            len_buffer = cursor.execute("SELECT COUNT(*) FROM buffer").fetchone()[0]
            if len_buffer > 0:
                cursor.execute(f"""
                    UPDATE age_stratification SET {column_name} = (
                        SELECT ID_SUBJECT
                        FROM buffer
                        WHERE rowid = age_stratification.rowid
                    )
                """)
        # for that year of inclusion, we also need to create a table for the 18-25 years old
        column_name = "incident_18_25_"+str(yoi)
        cursor.execute("DELETE FROM buffer")
        cursor.execute(f"""
            INSERT INTO buffer
            SELECT DISTINCT ID_SUBJECT
            FROM demographics
            WHERE
                (
                    /* at the year of inclusion, the patient must be alive (birth < yoi, death > yoi or null)*/
                    /* at the year of inclusion, the patient must fall into the inclusive age range */
                    ({yoi} - CAST(strftime('%Y', DT_BIRTH) as INT) BETWEEN 18 AND 25)
                    AND
                    (
                        (CAST(strftime('%Y', DT_DEATH) as INT) > {yoi})
                        OR
                        (DT_DEATH IS NULL)
                    )
                    /* Also, since I will work only with the subjects that appear in COHORTS, I can filter out the rest
                       When cohorts will consider every possible mental disorter, this condition will no nothing.
                       Else, it will filter out the subjects that do not have a record in the cohort table.
                    */
                    AND
                    ID_SUBJECT IN (SELECT DISTINCT ID_SUBJECT FROM cohorts)
                )
            ORDER BY ID_SUBJECT
        """)
        len_buffer = cursor.execute("SELECT COUNT(*) FROM buffer").fetchone()[0]
        if len_buffer > 0:
            cursor.execute(f"""
                UPDATE age_stratification SET {column_name} = (
                    SELECT ID_SUBJECT
                    FROM buffer
                    WHERE rowid = age_stratification.rowid
                )
            """)
    # get rid of the temporary table
    cursor.execute("DROP TABLE IF EXISTS buffer")
    cursor.execute("DROP TABLE IF EXISTS temp.buffer")
    # commit changes and close
    connection.commit()
    cursor.close()
    # hash and save hash
    write_to_slim_database_hash_file(
        hash_database_file(
            get_slim_database_filepath()
        )
    )
    print("done!")

##########################################
# STRATIFICATION UTILITIES
# which will be imported from other files
##########################################

from ..indicator.widget import AGE_WIDGET_INTERVALS

def stratify_demographics(connection: sqlite3.Connection, **kwargs) -> str:
    """ Given the internal ja database, stratify the patients according to the kwargs parameters.
    This function outputs a string, that is the name of the temporary table that stores the IDs of the patients that satisfy the conditions.
    The temporary table only has the column ID_SUBJECT of type TEXT.

    The returned table name will be in the format 'temp.<table_timestamp_name>'.

    After you are done with the output table, remember to drop it with the following command:

        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        connection.commit() 
    
    kwargs:
    - year_of_inclusion: int
        The year of inclusion of the patients in the cohort.
        If none provided, the current year. Must be present in age_stratification table.
    - age: list[tuple[int, int]]
        A list of age range ranges, such as [(18, 25), (45, 65)] or [(1, 14)].
        Must be compatible with the age_stratification table.
    - gender: str
        in ["A", "A-U", "M", "F", "U"]
    - civil_status: str
        in ["All", "All-Other", "Unmarried", "Married", "Married_no_long", "Other"]
    - job_condition: str
        in ["All", "All-Unknown", "Employed", "Unemployed", "Pension", "Unknown"]
    - educational_level: str
        in ["All", "All-Unknown", "0", "1", "2", "3", "4", "5", "6", "7", "8", "Unknown"]
        corresponds to the ISCED levels, where Unknown is synonym of ISCED level 9.
    """
    # inputs
    year_of_inclusion = int(kwargs.get("year_of_inclusion", time.localtime().tm_year))
    age_intervals_list = kwargs.get("age", None)
    if age_intervals_list is None:
        raise ValueError(f"List of age intervals must be provided. Found {age_intervals_list}")
    if not isinstance(age_intervals_list, list):
        raise ValueError(f"age must be a list. Found {age_intervals_list} (not a list)")
    if len(age_intervals_list) == 0:
        raise ValueError(f"age must be a non-empty list. Found {age_intervals_list}")
    for age_interval in age_intervals_list:
        if age_interval not in AGE_WIDGET_INTERVALS.values():
            raise ValueError(f"age must be a list of tuples[int, int] (inclusive) choosing from {AGE_WIDGET_INTERVALS.values()}. Found {age_interval}")
    _available_genders = ["A", "A-U", "M", "F", "U"]
    gender = kwargs.get("gender", None)
    if gender is None:
        raise ValueError(f"gender must be provided choosing from {_available_genders}")
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
    _available_educational_levels = ["All", "All-Unknown", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Unknown"]
    educational_level = kwargs.get("educational_level", None)
    if educational_level is None:
        raise ValueError("educational_level must be provided")
    if educational_level not in _available_educational_levels:
        raise ValueError(f"educational_level must be in {_available_educational_levels} and it must be a string")
    # logic
    cursor = connection.cursor()
    # check if the database has the necessary tables
    has_tables, missing_tables = check_database_has_tables(connection, cohorts_required=False, age_stratification_required=True)
    if not has_tables:
        raise ValueError(f"The database is missing the following tables: {missing_tables}")
    # create the table of stratified patients ids
    time_string = datetime.datetime.now().strftime("%H%M%S%f")
    table_name = "stratified_patients_" + time_string
    selection_string_from_age_startification_table = " UNION ".join(
        [
            f"""SELECT {get_age_stratification_column(year_of_inclusion, age_tuple)} AS ID_SUBJECT
            FROM age_stratification
            WHERE {get_age_stratification_column(year_of_inclusion, age_tuple)} IS NOT NULL"""
            for age_tuple in age_intervals_list
        ] 
    )
    if gender == "A":
        gender_selector_statement = "1"
    elif gender == "A-U":
        gender_selector_statement = f"GENDER IS NOT NULL"
    elif gender == "U":
        gender_selector_statement = f"GENDER IS NULL"
    else:
        gender_selector_statement = f"GENDER = '{str(gender)}'"
    if civil_status == "All":
        civil_status_selector_statement = "1"
    elif civil_status == "All-Other":
        civil_status_selector_statement = f"(CIVIL_STATUS != 'Other' AND CIVIL_STATUS IS NOT NULL)"
    else:
        civil_status_selector_statement = f"CIVIL_STATUS = '{civil_status}'"
    if job_condition == "All":
        job_condition_selector_statement = "1"
    elif job_condition == "All-Unknown":
        job_condition_selector_statement = f"JOB_COND IS NOT NULL"
    elif job_condition == "Unknown":
        job_condition_selector_statement = f"JOB_COND IS NULL"
    else:
        job_condition_selector_statement = f"JOB_COND = '{job_condition}'"
    if educational_level == "All":
        educational_level_selector_statement = "1"
    elif educational_level == "All-Unknown":
        educational_level_selector_statement = f"(EDU_LEVEL IS NOT NULL AND EDU_LEVEL != 9)"
    elif educational_level == "Unknown" or educational_level == "9":
        # 9 is the ISCED level for Unknown
        educational_level_selector_statement = f"(EDU_LEVEL IS NULL OR EDU_LEVEL = 9)"
    else:
        try:
            edu_level_int = int(educational_level)
        except ValueError:
            edu_level_int = 9
            print(f"WARNING: {educational_level} is not a valid educational level. Using 9 (Unknown) instead.")
        educational_level_selector_statement = f"EDU_LEVEL = {edu_level_int}"
    # database query
    cursor.execute(f"DROP TABLE IF EXISTS temp.{table_name};")
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} AS
        SELECT DISTINCT ID_SUBJECT FROM demographics
        WHERE
            /* ID_SUBJECT must be in the correct age interval */
            ID_SUBJECT IN ({selection_string_from_age_startification_table})
            AND
            /* ID_SUBJECT must satisfy the other conditions on gender, civil status, job condition, educational level */
            {gender_selector_statement}
            AND
            {civil_status_selector_statement}
            AND
            {job_condition_selector_statement}
            AND
            {educational_level_selector_statement}
    """)
    # do not commit, the table is temporary, don't want this table to be persistent
    cursor.close()
    return f"temp.{table_name}"

    



if __name__ == "__main__":
    print("This script is not intended to be run as the main script.")
        