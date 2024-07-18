import os, time, datetime
import pandas
import bokeh.palettes
import sqlite3

DATABASE_FILE = os.path.normpath(
    "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/ExampleData/Dati QUADIM - Standardizzati - Sicilia/DATABASE.db"
)







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


##################
# DATABASE OBJECT
##################

DB = sqlite3.connect(DATABASE_FILE)


##############
# UTILITIES
##############

### NOTE:
### SQLite stores temporary tables in a separate temp database. 
### It keeps that database in a separate file on disk, visible only to 
### the current database connection.
### The temporary database is deleted automatically as soon as the
### connection is closed.
### ->
### Good to store temporary query tables, and also age stratisfied tables

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
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [c[0] for c in cursor.fetchall()]
    missing_tables = [t for t in required_tables if t not in tables]
    cursor.close()  # close the cursor
    return len(missing_tables) == 0, missing_tables

#### incomplete
def add_cohorts_table(connection: sqlite3.Connection):
    """ Create the temporary cohorts table in the database.
    The table is created if it does not exist. If it does, it is replaced.
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
    # logic
    cursor = connection.cursor()
    # drop cohorts table if it exists
    cursor.execute("DROP TABLE IF EXISTS cohorts;")
    connection.commit()
    # create the cohorts table
    # the table has the following columns:
    # - ID_SUBJECT: alphanumeric (could be non-unique in the table)
    # - YEAR_ENTRY: integer
    # - AGE_ENTRY: integer
    # - ID_COHORT: string
    # - ID_DISORDER: string
    query = """
        CREATE TEMPORARY TABLE cohorts (
            ID_SUBJECT TEXT,
            YEAR_ENTRY INTEGER,
            AGE_ENTRY INTEGER,
            ID_COHORT TEXT,
            ID_DISORDER TEXT
        );
    """
    cursor.execute(query)
    connection.commit()
    # fill the table with the data
    ##################################################################################################################################


#### THEN GO BACK AND FIX MA1 AND TAB0 (GET_PLOT)
#### THEN TRY TO RUN THE DASHBOARD
#### IF IT WORKS, CORRECT EVERYTHING AND
#### DE COMMENT IN THE DISPATCHER THE COMMENTED INDICATORS


####
from ..indicator.widget import AGE_WIDGET_INTERVALS


def make_age_startification_tables(connection: sqlite3.Connection, year_of_inclusions_list: list[int]|None=None, age_stratifications: dict[str:tuple]|None=None, command: str="create"):
    """ Update the age stratification tables to speed up the process of stratifying by age.
        Age of patients is computed with respect to the year of inclusion.
        The created tables only contain the ID_SUBJECT of the patients that are in the age range.
        The tables are created if they do not exist, otherwise they are replaced.
        Tables are temporary, meaning they are deleted when the connection to the database is closed.

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
            The new tables will be called "demographics_<yoi>_<str>", where <yoi> is the year of inclusion (int) and <str> is the key.
            Each tuple has the following structure:
            (min_age_included, max_age_included)
        - command: str
            The command to execute. Can be "create" or "drop".
            If "create", the tables are created and overwritten if they exist.
            If "drop", the tables are dropped if they exist and are not created anew.
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
    # drop the tables if they exist
    all_tables = [a for a in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
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
    for year_of_inclusion in year_of_inclusions_list:
        for age_name, age_tuple in age_stratifications.items():
            table_name = f"demographics_{int(year_of_inclusion)}_{age_name}"
            #                                                                                 # if ypu remove '5 <=' it works fine! otherwide, it just takes all the available years...     
            cursor.execute(f"SELECT DISTINCT strftime('%Y', DT_BIRTH) FROM demographics WHERE (5 <= ({year_of_inclusion} - CAST(strftime('%Y', DT_BIRTH) as INT) ) <= 10)")
            l = [_[0] for _ in cursor.fetchall()]
            l.sort()
            print(year_of_inclusion)
            print(l)
            quit()

            # create the table
                # CREATE TEMPORARY TABLE '{table_name}' AS
            query = f"""
                    SELECT
                        DISTINCT ID_SUBJECT FROM demographics
                    WHERE 
                        (? <= ? - CAST(strftime('%Y', DT_BIRTH) as INT) <= ?)
            """
                        #     AND
                        #     (strftime('%Y', DT_DEATH) > ? OR DT_DEATH IS NULL)
            args = (year_of_inclusion-age_tuple[0], year_of_inclusion-age_tuple[1], year_of_inclusion)
            args = (age_tuple[0], year_of_inclusion, age_tuple[1]) ##
            cursor.execute(query, args) ####
            #######
            print(args, end=" ")
            print(len(cursor.fetchall()))
            print(cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
    connection.commit() # commit at each creation to not overload the memory
    
    #######
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("before closing the cursor", cursor.fetchall())
    # close the cursor
    cursor.close()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("after closing the cursor", cursor.fetchall())
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
        raise ValueError(f"age must be a list of strings choosing from {AGE_WIDGET_INTERVALS.keys()}. Found {age_intervals_list}")
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
        CREATE TEMPORARY TABLE {temp_table_name} AS
            SELECT * FROM demographics
            WHERE ID_SUBJECT IN ("""
    for i, age_interval in enumerate(age_intervals_list):
        query += f"SELECT ID_SUBJECT FROM 'demographics_{year_of_inclusion}_{age_interval}'"
        if i < len(age_intervals_list) - 1:
            query += " UNION "
    query += ")"
    ###
    print("CHECK THE STRATIFIED DEMOGRAPHICS TABLE")   ###################    here is the problemmm
    cursor.execute(f"SELECT COUNT(*) FROM 'demographics_{year_of_inclusion}_{age_intervals_list[0]}'")
    print(cursor.fetchall())
    print("QUERY 2 - stratify_demographics")
    print(query)
    cursor.execute(query)
    cursor.execute(f"SELECT COUNT(*) FROM {temp_table_name}")
    print(cursor.fetchall())
    #
    cursor.close()
    connection.close()
    quit()
    ###
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
        civil_status_selector_statement = f"(CIVIL_STATUS != 'Other')"
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
                SELECT DISTINCT ID_SUBJECT FROM {temp_table_name}
                WHERE
                    {gender_selector_statement}
                    AND
                    {civil_status_selector_statement}
                    AND
                    {job_condition_selector_statement}
                    AND
                    {educational_level_selector_statement}
    """
    queries.append(query)
    # QUERY 4: drop the temporary table temp_table
    queries.append(f"DROP TABLE IF EXISTS {temp_table_name};")
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
        