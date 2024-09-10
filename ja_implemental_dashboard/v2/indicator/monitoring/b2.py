import time
import numpy
import json
import sqlite3
import panel
from ..._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)
import bokeh.models
import bokeh.plotting

from ...database.database import DISEASE_CODE_TO_DB_CODE
from ...database.database import stratify_demographics, check_database_has_tables
from ..logic_utilities import clean_indicator_getter_input
from ..widget import indicator_widget, AGE_WIDGET_INTERVALS
from ...main_selectors.disease_text import DS_TITLE as DISEASES_LANGDICT
from ...caching.indicators import is_call_in_cache, retrieve_cached_json, cache_json





# indicator computation logic
def mb2(**kwargs):
    """
    output:
    dict[str: list[int]]
    keys level 0: ["01", "02", "03", "04", "05", "06", "07", "Other"] # TYPE_INT levels
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    connection: sqlite3.Connection = kwargs.get("connection", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    age = [AGE_WIDGET_INTERVALS[a] for a in age]
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    type_int_list = [1, 2, 3, 4, 5, 6, 7, 9]
    out_dict_key_list = type_int_list+["any_type"]
    mb2 = {k: 0 for k in out_dict_key_list}
    # logic
    # - first find stratified demographics (delete the table before return)
    stratified_demographics_table_name = stratify_demographics(
        connection=connection,
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    # open a cursor (close it before return)
    cursor = connection.cursor()
    # check if table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {stratified_demographics_table_name}")
    if cursor.fetchone()[0] == 0:
        return mb2
    # get the indicator values
    # first, get the value for any TYPE_INT in the 'interventions' table
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM interventions
        WHERE ID_PATIENT IN (
            /* Must be in the right stratification */
            /* Must have had the disease the year or after the year of inclusion */
            SELECT ID_PATIENT FROM {stratified_demographics_table_name}
            INTERSECT
            SELECT ID_PATIENT FROM cohorts WHERE 
                YEAR_OF_ONSET <= {year_of_inclusion} 
                AND 
                ID_DISORDER = '{disease_db_code}'
        )
        AND
        /* Here, TYPE_INT can be any */
        /* DT_INT year must be in the year of inclusion */
        CAST(strftime('%Y', DT_INT) AS INTEGER) = {year_of_inclusion}
    """)
    mb2["any_type"] = int(cursor.fetchone()[0])
    if mb2["any_type"] == 0:
        return mb2
    # first version: outer while loop
    for type_int_code in type_int_list:
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM interventions
            WHERE ID_PATIENT IN (
                /* Must be in the right stratification */
                /* Must have had the disease the year or after the year of inclusion */
                SELECT ID_PATIENT FROM {stratified_demographics_table_name}
                INTERSECT
                SELECT ID_PATIENT FROM cohorts WHERE 
                    YEAR_OF_ONSET <= {year_of_inclusion} 
                    AND 
                    ID_DISORDER = '{disease_db_code}'
            )
            AND
            /* Must have the TYPE_INT */
            {f"TYPE_INT = '{type_int_code}'" if type_int_code != 9 else f"TYPE_INT = {type_int_code} OR TYPE_INT IS NULL"}
            /* DT_INT year must be in the year of inclusion */
            CAST(strftime('%Y', DT_INT) AS INTEGER) = {year_of_inclusion}
        """)
        mb2[type_int_code] = int(cursor.fetchone()[0])
    # delete the table of stratified demograpohics
    cursor.execute(f"DROP TABLE IF EXISTS {stratified_demographics_table_name}")
    # close the cursor
    cursor.close()
    # return
    return mb2
    #
    #
    #
    #
    #
    #
    #  ATTENTION! THIS IS NOT READY YET
    #  IN FACT, IN THE ORIGINAL IMPLEMENTATION,
    #  FOR EACH TYPE_INT IT IS OBTAINED A LIST
    #  CONTAINING THE NUMBER OF INTERVENTIONS FOR EACH
    #  PATIENT DURING THE YEAR OF INCLUSION.
    #  THIS IS NEEDED BECAUSE THEN THE UI DISPLAYS
    #  THE MEAN, MEDIAN, Q1, Q3, AND IQR OF THE NUMBER
    #  OF INTERVENTIONS PER PATIENT, AS WELL AS THE
    #  DISTRIBUTION OF THE NUMBER OF INTERVENTIONS PER
    #  PATIENT.
    #
    #  SELECT COUNT() DOES NOT PROVIDE THIS INFORMATION
    #  INSTEAD, WE HAVE TO GET THE LIST OF CANDIDATE PATIENTS,
    #  AND THEN COUNT THE NUMBER OF INTERVENTIONS FOR EACH
    #  PATIENT, IN THE YEAR OF INCLUSION.
    #  
    #
    #
    #
    #
    #

# Indicator display
mb2_code = "MB2"
mb2_name_langdict = {
    "en": "Types of community interventions",
    "it": "Tipi di interventi comunitari",
    "fr": "Types d'interventions communautaires",
    "de": "Arten von Gemeinschaftseingriffen",
    "es": "Tipos de intervenciones comunitarias",
    "pt": "Tipos de intervenções comunitárias"
}
mb2_short_desription_langdict = {
    "en": 
        """
        Number of interventions delivered by Mental Health Outpatient Facilities
        by type of interventions.
        """,
    "it":
        """
        Numero di interventi erogati dalle strutture di salute mentale ambulatoriali
        per tipo di interventi.
        """,
    "fr":
        """
        Nombre d'interventions dispensées par les établissements de santé mentale ambulatoires
        par type d'interventions.
        """,
    "de":
        """
        Anzahl der Interventionen, die von ambulanten Einrichtungen für psychische Gesundheit
        nach Art der Interventionen durchgeführt wurden.
        """,
    "es":
        """
        Número de intervenciones entregadas por las instalaciones de salud mental ambulatorias
        por tipo de intervenciones.
        """,
    "pt":
        """
        Número de intervenções entregues por instalações de saúde mental ambulatoriais
        por tipo de intervenções.
        """
}


# other useful text
_year_langdict = {
    "en": "Year",
    "it": "Anno",
    "fr": "Année",
    "de": "Jahr",
    "es": "Año",
    "pt": "Ano"
}
_intervention_type_code_langdict = {
    "en": "Intervention type code",
    "it": "Codice del tipo di intervento",
    "fr": "Code du type d'intervention",
    "de": "Interventionstypcode",
    "es": "Código de tipo de intervención",
    "pt": "Código do tipo de intervenção"
}

_hover_tool_langdict = {
    "en": {
        "year": "Year",
        "intervention_type": "Intervention type",
        "count": "Total",
        "mean": "Mean",
        "median": "Median",
        "stdev": "Standard deviation",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Interquartile range",
    },
    "it": {
        "year": "Anno",
        "intervention_type": "Tipo di intervento",
        "count": "Totale",
        "mean": "Media",
        "median": "Mediana",
        "stdev": "Deviazione standard",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Intervallo interquartile",
    },
    "fr": {
        "year": "Année",
        "intervention_type": "Type d'intervention",
        "count": "Total",
        "mean": "Moyenne",
        "median": "Médiane",
        "stdev": "Écart-type",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Intervalle interquartile",
    },
    "de": {
        "year": "Jahr",
        "intervention_type": "Interventionstyp",
        "count": "Total",
        "mean": "Mittelwert",
        "median": "Median",
        "stdev": "Standardabweichung",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Interquartilbereich",
    },
    "es": {
        "year": "Año",
        "intervention_type": "Tipo de intervención",
        "count": "Total",
        "mean": "Media",
        "median": "Mediana",
        "stdev": "Desviación estándar",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Rango intercuartílico",
    },
    "pt": {
        "year": "Ano",
        "intervention_type": "Tipo de intervenção",
        "count": "Total",
        "mean": "Média",
        "median": "Mediana",
        "stdev": "Desvio padrão",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Intervalo interquartil",
    }
}

from ...database.database import INTERVENTIONS_CODES_LANGDICT_MAP, INTERVENTIONS_CODES_COLOR_DICT

_y_axis_langdict_all = {
    "en": "Total num. of interventions",
    "it": "Num. totale di interventi",
    "fr": "Nb. total d'interventions",
    "de": "Gesamtanzahl der Interventionen",
    "es": "Núm. total de intervenciones",
    "pt": "Num. total de intervenções"
}

_y_axis_langdict = {
    "en": "Num. of interventions per patient",
    "it": "Num. di interventi per paziente",
    "fr": "Nb. d'interventions par patient",
    "de": "Anzahl der Interventionen pro Patient",
    "es": "Núm. de intervenciones por paciente",
    "pt": "Num. de intervenções por paciente"
}

_all_interventions_langdict = {
    "en": "All interventions",
    "it": "Tutti gli interventi",
    "fr": "Toutes les interventions",
    "de": "Alle Interventionen",
    "es": "Todas las intervenciones",
    "pt": "Todas as intervenções"
}


# TABS
# - tab 0: indicator
# - tab 1: indicator distribution with boxplots
# - tab 2: indicator distribution with violin plots
# - tab 2: help
####################################################

mb2_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}

class mb2_tab0(object):
    def __init__(self, db_conn: sqlite3.Connection):
        self._language_code = "en"
        self._db_conn = db_conn
        # widgets
        self.widgets_instance = indicator_widget(
            language_code=self._language_code
        )
        # pane row
        self._pane_styles = {
        }
        self._pane_stylesheet = ""

    def get_plot(self, **kwargs):
        # inputs
        language_code = kwargs.get("language_code", self._language_code)
        disease_code = kwargs.get("disease_code", None)
        age_interval = self.widgets_instance.value["age"]
        age_interval_list = [AGE_WIDGET_INTERVALS[a] for a in age_interval]
        gender = self.widgets_instance.value["gender"]
        civil_status = self.widgets_instance.value["civil_status"]
        job_condition = self.widgets_instance.value["job_condition"]
        educational_level = self.widgets_instance.value["educational_level"]
        # logic
        # - cache check
        is_in_cache = is_call_in_cache(
            indicator_name=mb2_code,
            disease_code=disease_code,
            age_interval=age_interval_list,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        if is_in_cache:
            x_json, y_json = retrieve_cached_json(
                indicator_name=mb2_code,
                disease_code=disease_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            years_to_evaluate = [int(v) for v in json.loads(x_json)]
            y = json.loads(y_json)
            mb2_all = [int(v) for v in y["all"]]
            mb2_selected = [int(v) for v in y["selected"]]
            del y
        else:
            cursor = self._db_conn.cursor()
            # get the years of inclusion as all years from the first occurrence of the disease
            # for any patient up to the current year
            min_year_ = int(
                cursor.execute(f"""
                    SELECT MIN(YEAR_OF_ONSET) FROM cohorts
                    WHERE ID_DISORDER = '{DISEASE_CODE_TO_DB_CODE[disease_code]}'
                """).fetchone()[0]
            )
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            # get the indicator values (y-axis) for the years of inclusion (x-axis on the plot)
            mb2_all = []
            mb2_selected = []
            for year in years_to_evaluate:
                mb2_ = mb2(
                    connection=self._db_conn,
                    cohorts_required=True,
                    disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                    year_of_inclusion=year,
                    age=age_interval,
                    gender=gender,
                    civil_status=civil_status,
                    job_condition=job_condition,
                    educational_level=educational_level
                )
                mb2_all.append(mb2_["all"])
                mb2_selected.append(mb2_["selected"])
            # close cursor
            cursor.close()
            # cache the result
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "all": mb2_all,
                    "selected": mb2_selected
                }
            )
            cache_json(
                indicator_name=mb2_code,
                disease_code=disease_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level,
                x_json=x_json,
                y_json=y_json
            )
        # plot - use bokeh because it allows independent zooming
        _y_max_plot = max(max(mb2_all), max(mb2_selected))
        _y_max_plot *= 1.15
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_year_langdict[language_code], "@x"),
                (_number_of_patients_langdict[language_code], "@y")
            ]
        )
        plt_height = 350
        plot = bokeh.plotting.figure(
            sizing_mode="stretch_width",
            height=plt_height,
            title=mb2_code + " - " + mb2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code],
            x_axis_label=_year_langdict[language_code],
            x_range=(years_to_evaluate[0]-0.5, years_to_evaluate[-1]+0.5),
            y_axis_label=_number_of_patients_langdict[language_code],
            y_range=(0, _y_max_plot),
            tools="pan,wheel_zoom,box_zoom,reset,save",
            toolbar_location="right",
        )
        plot.xaxis.ticker = numpy.sort(years_to_evaluate)
        plot.xgrid.grid_line_color = None
        # plot of data
        plot.line(
            years_to_evaluate, mb2_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            line_color="#a0a0a0ff"
        )
        plot.circle(
            x=years_to_evaluate, 
            y=mb2_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            fill_color="#a0a0a0ff",
            line_width=0,
            size=10
        )
        plot.line(
            years_to_evaluate, mb2_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            line_color="#5D0E41ff" # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
        )
        plot.circle(
            years_to_evaluate, mb2_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            fill_color="#5D0E41ff", # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
            line_width=0,
            size=10
        )
        plot.add_tools(hover_tool)
        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        plot.toolbar.autohide = True
        plot.toolbar.logo = None
        out = panel.pane.Bokeh(plot, height=plt_height) # setting the height here solves the bug after first time it happens!!
        return out
    
    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", "_depression_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code=disease_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
        

mb2_tab_names_langdict["en"].append("Help")
mb2_tab_names_langdict["it"].append("Aiuto")
mb2_tab_names_langdict["fr"].append("Aide")
mb2_tab_names_langdict["de"].append("Hilfe")
mb2_tab_names_langdict["es"].append("Ayuda")
mb2_tab_names_langdict["pt"].append("Ajuda")


class mb2_tab1(object):
    def __init__(self):
        self._language_code = "en"
        # pane
        self._pane_styles = {
        }
        self._pane_stylesheet = ""
        self._panes: dict[str: panel.pane.HTML] = self._make_panes()

    def _make_panes(self):
        h3_style = """
            margin: 0px;
            margin-top: 10px;
            font-weight: 600;
            font-size: 1.15em;
            color: #555555;
        """
        p_style = """
            margin: 0px;
            margin-top: 2px;
            margin-left: 8px;
            margin-bottom: 6px;
            font-size: 0.95em;
            color: #777777;
        """
        html_langdict = {
            "en":
                f"""
                    <h3 style='{h3_style}'>Indicator Calculation</h3>
                    <p style='{p_style}'>
                    The treated incidence indicator calculates the number of patients
                    aged 18-25 years old
                    with an incident mental disorder (or newly taken-in-care)
                    treated in inpatient and outpatient Mental Health Facilities for each year
                    of data availability.
                    It takes into account various 
                    demographic factors such as year of inclusion, age, gender, civil status, 
                    job condition, and educational level.
                    </p>

                    <h3 style='{h3_style}'>Indicator Display</h3>
                    <p style='{p_style}'>
                    The indicator is displayed as a plot showing the number of patients 
                    over the years of data availability. The x-axis represents the years, 
                    and the y-axis represents the number of patients. 
                    The plot is stratified by disease, allowing you to select a specific disease 
                    to view its treated prevalence over time.
                    </p>
                """,
            "it":
                f"""
                    <h3 style='{h3_style}'>Calcolo dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore di incidenza trattata calcola il numero di pazienti
                    di età compresa tra 18 e 25 anni
                    con un disturbo mentale incidente (o appena presi in carico)
                    trattati in strutture di salute mentale ospedaliere e ambulatoriali
                    per ogni anno di disponibilità dei dati.
                    Considera vari fattori demografici come anno di inclusione, età, 
                    genere, stato civile, condizione lavorativa e livello di istruzione.
                    </p>

                    <h3 style='{h3_style}'>Visualizzazione dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è visualizzato come un grafico che mostra il numero di pazienti
                    nel corso degli anni di disponibilità dei dati. L'asse x rappresenta gli anni,
                    e l'asse y rappresenta il numero di pazienti.
                    Il grafico è stratificato per malattia, consentendo di selezionare una malattia specifica
                    per visualizzarne la prevalenza trattata nel tempo.
                    </p>
                """,
            "fr":
                f"""
                    <h3 style='{h3_style}'>Calcul de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur d'incidence traitée calcule le nombre de patients
                    âgés de 18 à 25 ans
                    atteints d'un trouble mental incident (ou nouvellement pris en charge)
                    traités dans des établissements de santé mentale hospitaliers et ambulatoires
                    pour chaque année de disponibilité des données.
                    Il prend en compte divers facteurs démographiques tels que l'année d'inclusion, l'âge,
                    le sexe, l'état civil, la condition d'emploi et le niveau d'éducation.
                    </p>

                    <h3 style='{h3_style}'>Affichage de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est affiché sous forme de graphique montrant le nombre de patients
                    au fil des années de disponibilité des données. L'axe des x représente les années,
                    et l'axe des y représente le nombre de patients.
                    Le graphique est stratifié par maladie, vous permettant de sélectionner une maladie spécifique
                    pour voir sa prévalence traitée au fil du temps.
                    </p>
                """,
            "de":
                f"""
                    <h3 style='{h3_style}'>Indikatorberechnung</h3>
                    <p style='{p_style}'>
                    Der Indikator für behandelte Inzidenz berechnet die Anzahl von Patienten
                    im Alter von 18 bis 25 Jahren
                    mit einer vorherrschenden psychischen Störung (oder neu aufgenommen)
                    behandelt in stationären und ambulanten Einrichtungen für psychische Gesundheit
                    für jedes Jahr der Datenverfügbarkeit.
                    Es berücksichtigt verschiedene demografische Faktoren wie das Jahr der Aufnahme, das Alter,
                    das Geschlecht, den Familienstand, den Beschäftigungszustand und das Bildungsniveau.
                    </p>

                    <h3 style='{h3_style}'>Anzeige des Indikators</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Diagramm dargestellt, das die Anzahl von Patienten zeigt
                    über die Jahre der Datenverfügbarkeit. Die x-Achse repräsentiert die Jahre,
                    und die y-Achse repräsentiert die Anzahl von Patienten.
                    Das Diagramm ist nach Krankheit stratifiziert, sodass Sie eine bestimmte Krankheit auswählen können
                    um ihre behandelte Prävalenz im Laufe der Zeit zu sehen.
                    </p>
                """,
            "es":
                f"""
                    <h3 style='{h3_style}'>Cálculo del indicador</h3>
                    <p style='{p_style}'>
                    El indicador de incidencia tratada calcula el número de pacientes
                    de 18 a 25 años
                    con un trastorno mental incidente (o recién atendidos)
                    tratados en instalaciones de salud mental hospitalarias y ambulatorias
                    para cada año de disponibilidad de datos.
                    Toma en cuenta varios factores demográficos como el año de inclusión, la edad,
                    el género, el estado civil, la condición laboral y el nivel educativo.
                    </p>

                    <h3 style='{h3_style}'>Visualización del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se muestra como un gráfico que muestra el número de pacientes
                    a lo largo de los años de disponibilidad de datos. El eje x representa los años,
                    y el eje y representa el número de pacientes.
                    El gráfico está estratificado por enfermedad, lo que le permite seleccionar una enfermedad específica
                    para ver su prevalencia tratada a lo largo del tiempo.
                    </p>
                """,
            "pt":
                f"""
                    <h3 style='{h3_style}'>Cálculo do indicador</h3>
                    <p style='{p_style}'>
                    O indicador de incidência tratada calcula o número de pacientes
                    com 18-25 anos
                    com um transtorno mental incidente (ou recém-atendidos)
                    tratados em instalações de saúde mental hospitalares e ambulatoriais
                    para cada ano de disponibilidade de dados.
                    Leva em consideração vários fatores demográficos como o ano de inclusão, a idade,
                    o gênero, o estado civil, a condição de trabalho e o nível educacional.
                    </p>

                    <h3 style='{h3_style}'>Visualização do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é exibido como um gráfico que mostra o número de pacientes
                    ao longo dos anos de disponibilidade de dados. O eixo x representa os anos,
                    e o eixo y representa o número de pacientes.
                    O gráfico é estratificado por doença, permitindo que você selecione uma doença específica
                    para ver sua prevalência tratada ao longo do tempo.
                    </p>
                """
        }
        panes = {
            lang: panel.pane.HTML(
                html_langdict[lang],
                styles={
                    "padding": "10px",
                    "padding-top": "0px",
                    "border": "1px solid rgb(211 227 253)",
                    "border-radius": "8px",
                }
            ) 
            for lang in html_langdict.keys()
        }
        return panes
    
    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code
        language_code = kwargs.get("language_code", "en")
        return self._panes[language_code]
   
    


if __name__ == "__main__":
    print("This module is not callable.")