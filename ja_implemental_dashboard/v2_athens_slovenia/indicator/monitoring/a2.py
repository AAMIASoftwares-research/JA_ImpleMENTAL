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
from ...loading.loading import increase_loading_counter, decrease_loading_counter





# indicator computation logic
def ma2(**kwargs):
    """
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
    ma2 = {
        "all": None,     # patients with any disease
        "selected": None # patients with the selected disease
    }
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
        # return
        ma2["all"] = 0
        ma2["selected"] = 0
        return ma2
    # get the indicator values
    # all patients
    all_ = int(
            cursor.execute(f"""
                SELECT COUNT(ID_SUBJECT) from COHORTS
                WHERE 
                    ID_SUBJECT IN (SELECT ID_SUBJECT FROM {stratified_demographics_table_name})
                    AND
                    YEAR_OF_ONSET = {int(year_of_inclusion)}
                    /* No check on the disease here */                   
            """).fetchone()[0]
    )
    # selected patients (with the disease)
    selected_ = int(
            cursor.execute(f"""
                SELECT COUNT(ID_SUBJECT) from COHORTS
                WHERE
                    ID_SUBJECT IN (SELECT ID_SUBJECT FROM {stratified_demographics_table_name})
                    AND
                    YEAR_OF_ONSET = {int(year_of_inclusion)}
                    AND
                    ID_DISORDER = '{disease_db_code}'
            """).fetchone()[0]
    )
    ma2["all"] = all_
    ma2["selected"] = selected_
    # delete the table of stratified demograpohics
    cursor.execute(f"DROP TABLE IF EXISTS {stratified_demographics_table_name}")
    # close the cursor
    cursor.close()
    # return
    return ma2


# Indicator display
ma2_code = "MA2"
ma2_name_langdict = {
    "en": "Treated incidence",
    "it": "Incidenza trattata",
    "fr": "Incidence traitée",
    "de": "Behandelte Inzidenz",
    "es": "Incidencia tratada",
    "pt": "Incidência tratada"
}
ma2_short_desription_langdict = {
    "en": 
        """Number of Patients with an incident mental disorder
            (or newly taken-in-care) treated in inpatient and outpatient
            Mental Health Facilities (for each year of data availability).
        """,
    "it":
        """Numero di pazienti con un disturbo mentale incidente
            (o appena presi in carico) trattati in strutture di salute mentale
            ospedaliere e ambulatoriali (per ogni anno di disponibilità dei dati).
        """,
    "fr":
        """Nombre de patients atteints d'un trouble mental incident
            (ou nouvellement pris en charge) traités dans des établissements de santé mentale
            hospitaliers et ambulatoires (pour chaque année de disponibilité des données).
        """,
    "de":
        """Anzahl der Patienten mit einer vorherrschenden psychischen Störung
            (oder neu aufgenommen) behandelt in stationären und ambulanten Einrichtungen
            für psychische Gesundheit (für jedes Jahr der Datenverfügbarkeit).
        """,
    "es":
        """Número de pacientes con un trastorno mental incidente
            (o recién ingresados) tratados en instalaciones de salud mental
            hospitalarias y ambulatorias (para cada año de disponibilidad de datos).
        """,  
    "pt":
        """Número de pacientes com um transtorno mental incidente
            (ou recém-atendidos) tratados em instalações de saúde mental
            hospitalares e ambulatoriais (para cada ano de disponibilidade de dados).
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
_number_of_patients_langdict = {
    "en": "Number of patients",
    "it": "Numero di pazienti",
    "fr": "Nombre de patients",
    "de": "Anzahl der Patienten",
    "es": "Número de pacientes",
    "pt": "Número de pacientes"
}

# TABS
#######

ma2_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}
#############################
class ma2_tab0(object):
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
            indicator_name=ma2_code,
            disease_code=disease_code,
            age_interval=age_interval_list,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        if is_in_cache:
            x_json, y_json = retrieve_cached_json(
                indicator_name=ma2_code,
                disease_code=disease_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            years_to_evaluate = [int(v) for v in json.loads(x_json)]
            y = json.loads(y_json)
            ma2_all = [int(v) for v in y["all"]]
            ma2_selected = [int(v) for v in y["selected"]]
            del y
        else:
            cursor = self._db_conn.cursor()
            # get the years of inclusion as all years from the first occurrence of the disease
            # for any patient up to the current year
            try:
                min_year_ = int(
                    cursor.execute(f"""
                        SELECT MIN(YEAR_OF_ONSET) FROM cohorts
                        WHERE ID_DISORDER = '{DISEASE_CODE_TO_DB_CODE[disease_code]}'
                    """).fetchone()[0]
                )
                min_year_available_ = True
            except:
                min_year_ = time.localtime().tm_year - 2
                min_year_available_ = False
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            # get the indicator values (y-axis) for the years of inclusion (x-axis on the plot)
            ma2_all = []
            ma2_selected = []
            for year in years_to_evaluate:
                ma2_ = ma2(
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
                ma2_all.append(ma2_["all"])
                ma2_selected.append(ma2_["selected"])
            # close cursor
            cursor.close()
            # cache the result
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "all": ma2_all,
                    "selected": ma2_selected
                }
            )
            cache_json(
                indicator_name=ma2_code,
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
        _y_max_plot = max(max(ma2_all), max(ma2_selected))
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
            title=ma2_code + " - " + ma2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code],
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
            years_to_evaluate, ma2_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            line_color="#a0a0a0ff"
        )
        plot.circle(
            x=years_to_evaluate, 
            y=ma2_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            fill_color="#a0a0a0ff",
            line_width=0,
            size=10
        )
        plot.line(
            years_to_evaluate, ma2_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            line_color="#A0153Eff" # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
        )
        plot.circle(
            years_to_evaluate, ma2_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            fill_color="#A0153Eff", # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
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
        

ma2_tab_names_langdict["en"].append("Help")
ma2_tab_names_langdict["it"].append("Aiuto")
ma2_tab_names_langdict["fr"].append("Aide")
ma2_tab_names_langdict["de"].append("Hilfe")
ma2_tab_names_langdict["es"].append("Ayuda")
ma2_tab_names_langdict["pt"].append("Ajuda")

class ma2_tab1(object):
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
                    Der behandelte Inzidenzindikator berechnet die Anzahl von Patienten
                    mit einer vorherrschenden psychischen Störung (oder neu aufgenommen)
                    behandelt in stationären und ambulanten Einrichtungen
                    für psychische Gesundheit für jedes Jahr der Datenverfügbarkeit.
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
                    con un trastorno mental incidente (o recién ingresados)
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