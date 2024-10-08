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
import holoviews
holoviews.extension('bokeh') # here holoviews is kept to create a BoxWhisker plot
                             # anda Violin plot, which are not available in Bokeh
                             # However, holoview plots for some reason get linked
                             # in the sense that if you move/zoom on one plot,
                             # also all other displayed plots move together.
                             # This is not the case with Bokeh plots, which are
                             # independent. This is why the line plot is done with Bokeh
                             # and the other two with Holoviews.
                             # In the future it would be better to have all plots
                             # done with Bokeh, but for now this is a workaround.
import bokeh.models
import bokeh.plotting

from ...database.database import DISEASE_CODE_TO_DB_CODE
from ...database.database import stratify_demographics, check_database_has_tables
from ..logic_utilities import clean_indicator_getter_input
from ..widget import indicator_widget, AGE_WIDGET_INTERVALS
from ...main_selectors.disease_text import DS_TITLE as DISEASES_LANGDICT
from ...caching.indicators import is_call_in_cache, retrieve_cached_json, cache_json
from ...main_selectors.cohort_text import COHORT_NAMES
from ...loading.loading import increase_loading_counter, decrease_loading_counter

# ATTENTION: THIS INDICATOR DOES NOT DEPEND ON THE DISEASE SELECTOR, AS THE DISEASE IS FIXED 
# _schizophrenia_

# indicator logic
def ea4(**kwargs):
    """
    output dict:
    - percentage (float): the indicator, ranage [0; 1]; 
    - distribution (list): the distribution of number of event per patient
    if the patient has at least one event of interest
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    connection: sqlite3.Connection = kwargs.get("connection", None)
    disease_db_code = DISEASE_CODE_TO_DB_CODE['_schizophrenia_']
    cohort_code = kwargs.get("cohort_code", None)
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    #
    # Access to treatment
    #
    output = {"percentage": 0.0, "distribution": []}
    # logic
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
        return output
    # get the indicator values
    # - first get the total of patients that
    #   satisfy the stratification and are in the cohort
    if cohort_code is None:
        print("WARNING: cohort_code is None in ea4.")
        cohort_code = "_a_"
    if cohort_code not in ["_a_", "_b_", "_c_"]:
        print("WARNING: cohort_code is not valid in ea4:", cohort_code)
        cohort_code = "_a_"
    if cohort_code == "_a_":
        cohort_condition_string = f"ID_DISORDER = '{disease_db_code}' AND YEAR_OF_ONSET <= {year_of_inclusion}"
    elif cohort_code == "_b_":
        cohort_condition_string = f"ID_DISORDER = '{disease_db_code}' AND YEAR_OF_ONSET = {year_of_inclusion}"
    elif cohort_code == "_c_":
        cohort_condition_string = f"""
            ID_DISORDER = '{disease_db_code}' 
            AND 
            YEAR_OF_ONSET = {year_of_inclusion} 
            AND
            ID_SUBJECT IN (
                SELECT {"incident_18_25_"+str(year_of_inclusion)} AS ID_SUBJECT 
                FROM age_stratification 
                WHERE {"incident_18_25_"+str(year_of_inclusion)} IS NOT NULL
            )
            """
    cursor.execute(f"""
        CREATE TEMPORARY TABLE temp_ea4 AS
        SELECT DISTINCT ID_SUBJECT 
        FROM {stratified_demographics_table_name}
        WHERE ID_SUBJECT IN (
            SELECT DISTINCT ID_SUBJECT FROM cohorts
                WHERE {cohort_condition_string}
        )
    """)
    total_ = int(cursor.execute(f"SELECT COUNT(*) FROM temp_ea4").fetchone()[0])
    # - from this list, find the number of patients that
    #   have at least one prescription of antipsychotic drugs during the year of evaluation
    cursor.execute(f"""
        CREATE TEMPORARY TABLE temp_ea4_2 AS
        SELECT DISTINCT ID_SUBJECT
        FROM temp_ea4
        WHERE ID_SUBJECT IN (
            SELECT DISTINCT ID_SUBJECT
            FROM pharma
            WHERE
                ID_SUBJECT IN (SELECT ID_SUBJECT FROM temp_ea4)
                AND
                strftime('%Y', DT_PRESCR) = '{year_of_inclusion}'
                AND
                ATC_CHAR LIKE 'N05A%' AND ATC_CHAR NOT LIKE 'N05AN%'
        )
        /*
        In this call, I don't have to worry about person characteristic, 
        disease, or cohort, as it is already taken care of 
        in the previous call.
        */
    """)
    numerator_ = int(cursor.execute(f"SELECT COUNT(*) FROM temp_ea4_2").fetchone()[0])
    # - calculate the percentage
    output["percentage"] = numerator_ / total_ if total_ > 0 else 0.0
    # - find the distribution of number of interventions per patient from the interventions table
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM pharma
        WHERE
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM temp_ea4_2)
            AND
            strftime('%Y', DT_PRESCR) = '{year_of_inclusion}'
            AND
            ATC_CHAR LIKE 'N05A%' AND ATC_CHAR NOT LIKE 'N05AN%'
        GROUP BY ID_SUBJECT
    """)
    distribution_ = [int(row[0]) for row in cursor.fetchall()]
    output["distribution"] = distribution_ if len(distribution_) > 0 else [0, 0]
    # delete the table of stratified demograpohics
    cursor.execute(f"DROP TABLE IF EXISTS {stratified_demographics_table_name}")
    cursor.execute("DROP TABLE IF EXISTS temp_ea4")
    cursor.execute("DROP TABLE IF EXISTS temp_ea4_2")
    # close the cursor
    cursor.close()
    # check output
    if output["percentage"] == 0.0:
        output["distribution"] = [0, 0]
    # return
    return output

# Indicator display
ea4_code = "EA4"
ea4_name_langdict = {
    "en": "Access to psychotropic treatment in schizophrenic disorders",
    "it": "Accesso al trattamento psicotropo nei disturbi schizofrenici",
    "fr": "Accès au traitement psychotrope dans les troubles schizophréniques",
    "de": "Zugang zur psychotropen Behandlung bei schizophrenen Störungen",
    "es": "Acceso al tratamiento psicotrópico en trastornos esquizofrénicos",
    "pt": "Acesso ao tratamento psicotrópico em transtornos esquizofrênicos"
}
ea4_short_desription_langdict = {
    "en": """Percentage of patients with schizophrenic disorder receiving at least one prescription of antipsychotic drugs during the year of evaluation.""",
    "it": """Percentuale di pazienti con disturbo schizofrenico che ricevono almeno una prescrizione di farmaci antipsicotici durante l'anno di valutazione.""",
    "fr": """Pourcentage de patients atteints de trouble schizophrénique recevant au moins une prescription de médicaments antipsychotiques pendant l'année d'évaluation.""",
    "de": """Prozentsatz der Patienten mit schizophrenen Störungen, die während des Bewertungsjahres mindestens ein Rezept für Antipsychotika erhalten.""",
    "es": """Porcentaje de pacientes con trastorno esquizofrénico que reciben al menos una receta de medicamentos antipsicóticos durante el año de evaluación.""",
    "pt": """Percentagem de pacientes com transtorno esquizofrênico que recebem pelo menos uma prescrição de medicamentos antipsicóticos durante o ano de avaliação."""
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
_percentage_of_patients_langdict = {
    "en": "Percentage of patients",
    "it": "Percentuale di pazienti",
    "fr": "Pourcentage de patients",
    "de": "Prozentsatz der Patienten",
    "es": "Porcentaje de pacientes",
    "pt": "Percentagem de pacientes"
}
_number_of_interventions_langdict = {
    "en": "Num. of prescriptions per patient",
    "it": "Num. di prescrizioni per paziente",
    "fr": "Nb. de prescriptions par patient",
    "de": "Anzahl der Verschreibungen pro Patient",
    "es": "Núm. de recetas por paciente",
    "pt": "Num. de prescrições por paciente"
}

_hover_tool_langdict = {
    "en": {
        "year": "Year",
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
        "count": "Total",
        "mean": "Média",
        "median": "Mediana",
        "stdev": "Desvio padrão",
        "q1": "Q1 (25%)",
        "q3": "Q3 (75%)",
        "iqr": "Intervalo interquartil",
    }
}

# TABS
# - tab 0: indicator
# - tab 1: indicator distribution with boxplots
# - tab 2: indicator distribution with violin plots
# - tab 2: help
####################################################

ea4_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}

class ea4_tab0(object):
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
        cohort_code = kwargs.get("cohort_code", None)
        age_interval = self.widgets_instance.value["age"]
        age_interval_list = [AGE_WIDGET_INTERVALS[a] for a in age_interval]
        gender = self.widgets_instance.value["gender"]
        civil_status = self.widgets_instance.value["civil_status"]
        job_condition = self.widgets_instance.value["job_condition"]
        educational_level = self.widgets_instance.value["educational_level"]
        # logic
        is_in_cache = is_call_in_cache(
            indicator_name=ea4_code,
            disease_code=disease_code,
            cohort=cohort_code,
            age_interval=age_interval_list,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        if is_in_cache:
            x_json, y_json = retrieve_cached_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            years_to_evaluate = [int(v) for v in json.loads(x_json)]
            y = json.loads(y_json)
            # encode for plotting
            ea4_list = [100*float(v) for v in y["percentage"]]
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
            cursor.close()
            ea4_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea4_ = ea4(
                    connection=self._db_conn,
                    disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                    cohort_code=cohort_code,
                    year_of_inclusion=year,
                    age=age_interval_list,
                    gender=gender,
                    civil_status=civil_status,
                    job_condition=job_condition,
                    educational_level=educational_level
                )
                ea4_list.append(ea4_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea4_["percentage"] for ea4_ in ea4_list],
                    "distribution": [ea4_["distribution"] for ea4_ in ea4_list]
                }
            )
            cache_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level,
                x_json=x_json,
                y_json=y_json
            )
            # encode for plotting
            ea4_list = [100*ea4_["percentage"] for ea4_ in ea4_list]
        # plot - use bokeh because it allows independent zooming
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_year_langdict[language_code], "@x"),
                (_percentage_of_patients_langdict[language_code], "@y%")
            ]
        )
        plot = bokeh.plotting.figure(
            sizing_mode="stretch_width",
            height=350,
            title=ea4_code + " - " + ea4_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
            x_axis_label=_year_langdict[language_code],
            x_range=(years_to_evaluate[0]-0.5, years_to_evaluate[-1]+0.5),
            y_axis_label=_percentage_of_patients_langdict[language_code],
            y_range=(-0.5, 100.5),
            tools="pan,wheel_zoom,box_zoom,reset,save",
            toolbar_location="right",
        )
        plot.xaxis.ticker = numpy.sort(years_to_evaluate)
        plot.xgrid.grid_line_color = None
        plot.yaxis[0].formatter = bokeh.models.PrintfTickFormatter(format="%.0f%%")
        plot.line(
            years_to_evaluate, ea4_list,
            line_color="#82CD47FF" # https://colorhunt.co/palette/f0ff4282cd4754b435379237
        )
        plot.scatter(
            years_to_evaluate, ea4_list,
            fill_color="#82CD47FF", # https://colorhunt.co/palette/f0ff4282cd4754b435379237
            line_width=0,
            size=10
        )
        plot.add_tools(hover_tool)
        plot.toolbar.autohide = True
        plot.toolbar.logo = None
        out = panel.pane.Bokeh(plot)
        #
        return out

    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code
        language_code = kwargs.get("language_code", "en")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code="_schizophrenia_",
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane

#

ea4_tab_names_langdict["en"].append("Indicator distribution boxplot")
ea4_tab_names_langdict["it"].append("Distribuzione dell'indicatore con boxplot")
ea4_tab_names_langdict["fr"].append("Distribution de l'indicateur avec boxplot")
ea4_tab_names_langdict["de"].append("Indikatorverteilung Boxplot")
ea4_tab_names_langdict["es"].append("Distribución del indicador con boxplot")
ea4_tab_names_langdict["pt"].append("Distribuição do indicador com boxplot")

class ea4_tab1(object):
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
        cohort_code = kwargs.get("cohort_code", None)
        age_interval = self.widgets_instance.value["age"]
        age_interval_list = [AGE_WIDGET_INTERVALS[a] for a in age_interval]
        gender = self.widgets_instance.value["gender"]
        civil_status = self.widgets_instance.value["civil_status"]
        job_condition = self.widgets_instance.value["job_condition"]
        educational_level = self.widgets_instance.value["educational_level"]
        # logic
        is_in_cache = is_call_in_cache(
            indicator_name=ea4_code,
            disease_code=disease_code,
            cohort=cohort_code,
            age_interval=age_interval_list,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        if is_in_cache:
            x_json, y_json = retrieve_cached_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            years_to_evaluate = [int(v) for v in json.loads(x_json)]
            y = json.loads(y_json)
            # encode for plotting
            ea4_dist_list = [[int(n) for n in v] for v in y["distribution"]]
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
            cursor.close()
            ea4_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea4_ = ea4(
                    connection=self._db_conn,
                    disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                    cohort_code=cohort_code,
                    year_of_inclusion=year,
                    age=age_interval_list,
                    gender=gender,
                    civil_status=civil_status,
                    job_condition=job_condition,
                    educational_level=educational_level
                )
                ea4_list.append(ea4_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea4_["percentage"] for ea4_ in ea4_list],
                    "distribution": [ea4_["distribution"] for ea4_ in ea4_list]
                }
            )
            cache_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level,
                x_json=x_json,
                y_json=y_json
            )
            # encode for plotting
            ea4_dist_list = [l["distribution"] for l in ea4_list]
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea4_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea4_dist_list[i])
        plot = holoviews.BoxWhisker(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False, 
            box_fill_color="#d3e3fd", 
            title=ea4_code + " - " + ea4_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea4_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea4_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea4_dist_list[i], 75) - numpy.percentile(ea4_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
        })
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_hover_tool_langdict[language_code]["year"], "@year"),
                (_hover_tool_langdict[language_code]["count"], "@count"),
                (_hover_tool_langdict[language_code]["mean"], "@mean{0.0}"),
                (_hover_tool_langdict[language_code]["median"], "@median{0.0}"),
                (_hover_tool_langdict[language_code]["stdev"], "@stdev{0.0}"),
                (_hover_tool_langdict[language_code]["q1"], "@q1{0.0}"),
                (_hover_tool_langdict[language_code]["q3"], "@q3{0.0}"),
                (_hover_tool_langdict[language_code]["iqr"], "@iqr{0.0}"),
            ]
        )
        bk_hover_glyph = bokeh_plot.vspan(
            x="year", 
            source=source,
            line_width=40,
            line_color="#00000000"
        )
        bokeh_plot.add_tools(hover_tool)
        hover_tool.renderers = [bk_hover_glyph]
        # final bokeh options
        bokeh_plot.sizing_mode="stretch_width"
        bokeh_plot.height=350
        bokeh_plot.toolbar.autohide = True
        bokeh_plot.toolbar.logo = None
        #
        return panel.pane.Bokeh(bokeh_plot)
        
    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", "_schizophrenia_")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code="_schizophrenia_",
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
#
    

ea4_tab_names_langdict["en"].append("Indicator distribution violin plot")
ea4_tab_names_langdict["it"].append("Distribuzione dell'indicatore con violino")
ea4_tab_names_langdict["fr"].append("Distribution de l'indicateur avec violon")
ea4_tab_names_langdict["de"].append("Indikatorverteilung Geigenplot")
ea4_tab_names_langdict["es"].append("Distribución del indicador con violín")
ea4_tab_names_langdict["pt"].append("Distribuição do indicador com violino")

class ea4_tab2(object):
    def __init__(self, connection: dict):
        self._language_code = "en"
        self._db_conn = connection
        self.widgets_instance = indicator_widget(
             language_code=self._language_code,
        )
        # pane row
        self._pane_styles = {
        }
        self._pane_stylesheet = ""

    def get_plot(self, **kwargs):
        # inputs
        language_code = kwargs.get("language_code", self._language_code)
        disease_code = kwargs.get("disease_code", None)
        cohort_code = kwargs.get("cohort_code", None)
        age_interval = self.widgets_instance.value["age"]
        age_interval_list = [AGE_WIDGET_INTERVALS[a] for a in age_interval]
        gender = self.widgets_instance.value["gender"]
        civil_status = self.widgets_instance.value["civil_status"]
        job_condition = self.widgets_instance.value["job_condition"]
        educational_level = self.widgets_instance.value["educational_level"]
        # logic
        is_in_cache = is_call_in_cache(
            indicator_name=ea4_code,
            disease_code=disease_code,
            cohort=cohort_code,
            age_interval=age_interval_list,
            gender=gender,
            civil_status=civil_status,
            job_condition=job_condition,
            educational_level=educational_level
        )
        if is_in_cache:
            x_json, y_json = retrieve_cached_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            years_to_evaluate = [int(v) for v in json.loads(x_json)]
            y = json.loads(y_json)
            # encode for plotting
            ea4_dist_list = [[int(n) for n in v] for v in y["distribution"]]
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
            cursor.close()
            ea4_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea4_ = ea4(
                    connection=self._db_conn,
                    disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                    cohort_code=cohort_code,
                    year_of_inclusion=year,
                    age=age_interval_list,
                    gender=gender,
                    civil_status=civil_status,
                    job_condition=job_condition,
                    educational_level=educational_level
                )
                ea4_list.append(ea4_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea4_["percentage"] for ea4_ in ea4_list],
                    "distribution": [ea4_["distribution"] for ea4_ in ea4_list]
                }
            )
            cache_json(
                indicator_name=ea4_code,
                disease_code=disease_code,
                cohort=cohort_code,
                age_interval=age_interval_list,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level,
                x_json=x_json,
                y_json=y_json
            )
            # encode for plotting
            ea4_dist_list = [l["distribution"] for l in ea4_list]
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea4_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea4_dist_list[i])
        plot = holoviews.Violin(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False,
            inner="quartiles",
            bandwidth=0.5,
            violin_color="#d3e3fd", 
            title=ea4_code + " - " + ea4_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea4_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea4_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea4_dist_list[i], 75) - numpy.percentile(ea4_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea4_dist_list[i]) for i in range(len(years_to_evaluate))],
        })
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_hover_tool_langdict[language_code]["year"], "@year"),
                (_hover_tool_langdict[language_code]["count"], "@count"),
                (_hover_tool_langdict[language_code]["mean"], "@mean{0.0}"),
                (_hover_tool_langdict[language_code]["median"], "@median{0.0}"),
                (_hover_tool_langdict[language_code]["stdev"], "@stdev{0.0}"),
                (_hover_tool_langdict[language_code]["q1"], "@q1{0.0}"),
                (_hover_tool_langdict[language_code]["q3"], "@q3{0.0}"),
                (_hover_tool_langdict[language_code]["iqr"], "@iqr{0.0}"),
            ]
        )
        bk_hover_glyph = bokeh_plot.vspan(
            x="year", 
            source=source,
            line_width=40,
            line_color="#00000000"
        )
        bokeh_plot.add_tools(hover_tool)
        hover_tool.renderers = [bk_hover_glyph]
        # final bokeh options
        bokeh_plot.sizing_mode="stretch_width"
        bokeh_plot.height=350
        bokeh_plot.toolbar.autohide = True
        bokeh_plot.toolbar.logo = None
        #
        return panel.pane.Bokeh(bokeh_plot)
        
    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", "_schizophrenia_")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code="_schizophrenia_",
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
#

ea4_tab_names_langdict["en"].append("Help")
ea4_tab_names_langdict["it"].append("Aiuto")
ea4_tab_names_langdict["fr"].append("Aide")
ea4_tab_names_langdict["de"].append("Hilfe")
ea4_tab_names_langdict["es"].append("Ayuda")
ea4_tab_names_langdict["pt"].append("Ajuda")


class ea4_tab3(object):
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
                    The indicator is calculated as the percentage of patients having at least one prescription of antipsychotic drugs in the year of inclusion.
                    The denominator is the number of patients that satisfy the variuos stratification parameters and have the disturb of interest, 
                    and the numerator is the number of patients with at least one prescription in the year that are included in
                    the set of patients used to compute the denominator.
                    It takes into account various 
                    demographic factors such as year of inclusion, age, gender, civil status, 
                    job condition, and educational level.
                    </p>

                    <h3 style='{h3_style}'>Indicator Display</h3>
                    <p style='{p_style}'>
                    The indicator is displayed as a plot showing the percentage of patients having at least one
                    prescription over the years of data availability. The x-axis represents the years,
                    and the y-axis represents the percentage of patients. 
                    The indicator is also displayed as a boxplot and a violin plot showing the distribution
                    of the number of events of interest per patient, provided that the patient has at least one event
                    in the year.
                    </p>
                """,
            "it":
                f"""
                    <h3 style='{h3_style}'>Calcolo dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è calcolato come la percentuale di pazienti che hanno almeno una prescrizione di farmaci antipsicotici nell'anno di inclusione.
                    Il denominatore è il numero di pazienti che soddisfano i vari parametri di stratificazione e hanno il disturbo di interesse,
                    e il numeratore è il numero di pazienti con almeno una prescrizione nell'anno che sono inclusi nel
                    insieme di pazienti utilizzato per calcolare il denominatore.
                    Si tiene conto di vari fattori demografici come l'anno di inclusione, l'età, il genere, lo stato civile,
                    condizione lavorativa e livello di istruzione.
                    </p>

                    <h3 style='{h3_style}'>Visualizzazione dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è visualizzato come un grafico che mostra la percentuale di pazienti che hanno almeno una
                    prescrizione nel corso degli anni di disponibilità dei dati. L'asse x rappresenta gli anni,
                    e l'asse y rappresenta la percentuale di pazienti.
                    L'indicatore è anche visualizzato come un boxplot e un violino che mostrano la distribuzione
                    del numero di interventi per paziente, a condizione che il paziente abbia almeno un intervento
                    nell'anno.
                    </p>
                """,
            "fr":
                f"""
                    <h3 style='{h3_style}'>Calcul de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est calculé comme le pourcentage de patients ayant au moins une prescription de médicaments antipsychotiques l'année de l'inclusion.
                    Le dénominateur est le nombre de patients qui satisfont aux différents paramètres de stratification et ont le trouble d'intérêt,
                    et le numérateur est le nombre de patients ayant au moins une prescription dans l'année qui sont inclus dans
                    l'ensemble de patients utilisé pour calculer le dénominateur.
                    Il tient compte de divers facteurs démographiques tels que l'année d'inclusion, l'âge, le sexe, l'état civil,
                    condition d'emploi et niveau d'éducation.
                    </p>

                    <h3 style='{h3_style}'>Affichage de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est affiché sous forme de graphique montrant le pourcentage de patients ayant au moins une
                    prescription au fil des années de disponibilité des données. L'axe des x représente les années,
                    et l'axe des y représente le pourcentage de patients.
                    L'indicateur est également affiché sous forme de boîte à moustaches et de violon montrant la distribution
                    du nombre d'interventions par patient, à condition que le patient ait au moins une intervention
                    dans l'année.
                    </p>
                """,
            "de":
                f"""
                    <h3 style='{h3_style}'>Indikatorberechnung</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Prozentsatz der Patienten berechnet, die im Jahr der Aufnahme mindestens ein Rezept für Antipsychotika erhalten.
                    Der Nenner ist die Anzahl der Patienten, die die verschiedenen Stratifikationsparameter erfüllen und die Störung von Interesse haben,
                    und der Zähler ist die Anzahl der Patienten mit mindestens einem Rezept im Jahr, die inbegriffen sind
                    die Gruppe von Patienten, die zur Berechnung des Nenners verwendet werden.
                    Es werden verschiedene demografische Faktoren berücksichtigt, wie das Jahr der Aufnahme, das Alter, das Geschlecht, der Familienstand,
                    Beschäftigungsstatus und Bildungsniveau.
                    </p>

                    <h3 style='{h3_style}'>Anzeige des Indikators</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Diagramm dargestellt, das den Prozentsatz der Patienten zeigt, die mindestens eine
                    Verschreibung im Laufe der Jahre der Datenverfügbarkeit erhalten. Die x-Achse repräsentiert die Jahre,
                    und die y-Achse repräsentiert den Prozentsatz der Patienten.
                    Der Indikator wird auch als Boxplot und Violinplot dargestellt, die die Verteilung zeigen
                    der Anzahl der Interventionen pro Patient, vorausgesetzt, der Patient hat mindestens eine Intervention
                    im Jahr.
                    </p>
                """,
            "es":
                f"""
                    <h3 style='{h3_style}'>Cálculo del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se calcula como el porcentaje de pacientes que tienen al menos una receta de medicamentos antipsicóticos en el año de inclusión.
                    El denominador es el número de pacientes que cumplen con los diversos parámetros de estratificación y tienen el trastorno de interés,
                    y el numerador es el número de pacientes con al menos una receta en el año que están incluidos en
                    el conjunto de pacientes utilizado para calcular el denominador.
                    Se tienen en cuenta varios factores demográficos como el año de inclusión, la edad, el género, el estado civil,
                    condición laboral y nivel educativo.
                    </p>

                    <h3 style='{h3_style}'>Visualización del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se muestra como un gráfico que muestra el porcentaje de pacientes que tienen al menos una
                    receta a lo largo de los años de disponibilidad de datos. El eje x representa los años,
                    y el eje y representa el porcentaje de pacientes.
                    El indicador también se muestra como un diagrama de caja y un violín que muestran la distribución
                    del número de intervenciones por paciente, siempre que el paciente tenga al menos una intervención
                    en el año.
                    </p>
                """,
            "pt":
                f"""
                    <h3 style='{h3_style}'>Cálculo do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é calculado como a porcentagem de pacientes que têm pelo menos uma prescrição de medicamentos antipsicóticos no ano de inclusão.
                    O denominador é o número de pacientes que satisfazem os vários parâmetros de estratificação e têm o distúrbio de interesse,
                    e o numerador é o número de pacientes com pelo menos uma prescrição no ano que estão incluídos em
                    o conjunto de pacientes usado para calcular o denominador.
                    São considerados vários fatores demográficos como o ano de inclusão, a idade, o sexo, o estado civil,
                    condição de trabalho e nível educacional.
                    </p>

                    <h3 style='{h3_style}'>Visualização do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é exibido como um gráfico que mostra a porcentagem de pacientes que têm pelo menos uma
                    prescrição ao longo dos anos de disponibilidade de dados. O eixo x representa os anos,
                    e o eixo y representa a porcentagem de pacientes.
                    O indicador também é exibido como um boxplot e um violino que mostram a distribuição
                    do número de intervenções por paciente, desde que o paciente tenha pelo menos uma intervenção
                    no ano.
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
