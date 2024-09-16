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


# indicator logic
def ea2(**kwargs):
    """
    output dict:
    - percentage (float): the indicator, ranage [0; 1]; 
    - distribution (list): the distribution of number of intervention per patient
    if the patient has at least one intervention
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    connection: sqlite3.Connection = kwargs.get("connection", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    cohort_code = kwargs.get("cohort_code", None)
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    #
    # Access to community care
    # Percentage of patients with at least one outpatient 
    # community contact.
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
        print("WARNING: cohort_code is None in ea2.")
        cohort_code = "_a_"
    if cohort_code not in ["_a_", "_b_", "_c_"]:
        print("WARNING: cohort_code is not valid in ea2:", cohort_code)
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
        CREATE TEMPORARY TABLE temp_ea2 AS
        SELECT DISTINCT(ID_SUBJECT) 
        FROM {stratified_demographics_table_name}
        WHERE ID_SUBJECT IN (
            SELECT DISTINCT ID_SUBJECT FROM cohorts
                WHERE {cohort_condition_string}
        )
    """)
    total_ = int(cursor.execute(f"SELECT COUNT(*) FROM temp_ea2").fetchone()[0])
    # - from this list, find the number of patients that
    #   have at least one intervention of any kind in the year of inclusion
    cursor.execute(f"""
        CREATE TEMPORARY TABLE temp_ea2_2 AS
        SELECT DISTINCT ID_SUBJECT
        FROM temp_ea2
        WHERE ID_SUBJECT IN (
            SELECT DISTINCT ID_SUBJECT
            FROM interventions
            WHERE 
                strftime('%Y', DT_INT) = '{year_of_inclusion}'
                AND
                TYPE_INT = 4
        )
        /*
        In this call, I don't have to worry about person characteristic, 
        disease, or cohort, as it is already taken care of 
        in the previous call.
        */
    """)
    numerator_ = int(cursor.execute(f"SELECT COUNT(*) FROM temp_ea2_2").fetchone()[0])
    # - calculate the percentage
    output["percentage"] = numerator_ / total_ if total_ > 0 else 0.0
    # - find the distribution of number of interventions per patient from the interventions table
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM interventions
        WHERE 
            ID_SUBJECT IN (SELECT ID_SUBJECT FROM temp_ea2_2)
            AND
            strftime('%Y', DT_INT) = '{year_of_inclusion}'
            AND
            TYPE_INT = 4
        GROUP BY ID_SUBJECT
    """)
    distribution_ = [int(row[0]) for row in cursor.fetchall()]
    output["distribution"] = distribution_ if len(distribution_) > 0 else [0, 0]
    # delete the table of stratified demograpohics
    cursor.execute(f"DROP TABLE IF EXISTS {stratified_demographics_table_name}")
    cursor.execute("DROP TABLE IF EXISTS temp_ea2")
    cursor.execute("DROP TABLE IF EXISTS temp_ea2_2")
    # close the cursor
    cursor.close()
    # check output
    if output["percentage"] == 0.0:
        output["distribution"] = [0, 0]
    # return
    return output

# Indicator display
ea2_code = "EA2"
ea2_name_langdict = {
    "en": "Access to psychosocial care in the community",
    "it": "Accesso alle cure psicosociali nella comunità",
    "fr": "Accès aux soins psychosociaux dans la communauté",
    "de": "Zugang zu psychosozialer Versorgung in der Gemeinde",
    "es": "Acceso a la atención psicosocial en la comunidad",
    "pt": "Acesso aos cuidados psicossociais na comunidade"
}
ea2_short_desription_langdict = {
    "en": """Percentage of patients with at least one psychosocial intervention.""",
    "it": """Percentuale di pazienti con almeno un intervento psicosociale.""",
    "fr": """Pourcentage de patients avec au moins une intervention psychosociale.""",
    "de": """Prozentsatz der Patienten mit mindestens einem psychosozialen Eingriff.""",
    "es": """Porcentaje de pacientes con al menos una intervención psicosocial.""",
    "pt": """Percentagem de pacientes com pelo menos uma intervenção psicossocial."""
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
    "en": "Num. of interventions per patient",
    "it": "Num. di interventi per paziente",
    "fr": "Nb. d'interventions par patient",
    "de": "Anzahl der Interventionen pro Patient",
    "es": "Num. de intervenciones por paciente",
    "pt": "Num. de intervenções por paciente"
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

ea2_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}

class ea2_tab0(object):
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
            indicator_name=ea2_code,
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
                indicator_name=ea2_code,
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
            ea2_list = [100*float(v) for v in y["percentage"]]
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
            ea2_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea2_ = ea2(
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
                ea2_list.append(ea2_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea2_["percentage"] for ea2_ in ea2_list],
                    "distribution": [ea2_["distribution"] for ea2_ in ea2_list]
                }
            )
            cache_json(
                indicator_name=ea2_code,
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
            ea2_list = [100*ea2_["percentage"] for ea2_ in ea2_list]
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
            title=ea2_code + " - " + ea2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
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
            years_to_evaluate, ea2_list,
            line_color="#A0153Eff" # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
        )
        plot.circle(
            years_to_evaluate, ea2_list,
            fill_color="#A0153Eff", # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
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
        disease_code = kwargs.get("disease_code", "_depression_")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code=disease_code,
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane

#

ea2_tab_names_langdict["en"].append("Indicator distribution boxplot")
ea2_tab_names_langdict["it"].append("Distribuzione dell'indicatore con boxplot")
ea2_tab_names_langdict["fr"].append("Distribution de l'indicateur avec boxplot")
ea2_tab_names_langdict["de"].append("Indikatorverteilung Boxplot")
ea2_tab_names_langdict["es"].append("Distribución del indicador con boxplot")
ea2_tab_names_langdict["pt"].append("Distribuição do indicador com boxplot")

class ea2_tab1(object):
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
            indicator_name=ea2_code,
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
                indicator_name=ea2_code,
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
            ea2_dist_list = [[int(n) for n in v] for v in y["distribution"]]
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
            ea2_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea2_ = ea2(
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
                ea2_list.append(ea2_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea2_["percentage"] for ea2_ in ea2_list],
                    "distribution": [ea2_["distribution"] for ea2_ in ea2_list]
                }
            )
            cache_json(
                indicator_name=ea2_code,
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
            ea2_dist_list = [l["distribution"] for l in ea2_list]
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea2_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea2_dist_list[i])
        plot = holoviews.BoxWhisker(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False, 
            box_fill_color="#d3e3fd", 
            title=ea2_code + " - " + ea2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea2_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea2_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea2_dist_list[i], 75) - numpy.percentile(ea2_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
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
        disease_code = kwargs.get("disease_code", "_depression_")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code=disease_code,
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
#
    

ea2_tab_names_langdict["en"].append("Indicator distribution violin plot")
ea2_tab_names_langdict["it"].append("Distribuzione dell'indicatore con violino")
ea2_tab_names_langdict["fr"].append("Distribution de l'indicateur avec violon")
ea2_tab_names_langdict["de"].append("Indikatorverteilung Geigenplot")
ea2_tab_names_langdict["es"].append("Distribución del indicador con violín")
ea2_tab_names_langdict["pt"].append("Distribuição do indicador com violino")

class ea2_tab2(object):
    def __init__(self, dict_of_tables: dict):
        self._language_code = "en"
        self._dict_of_tables = dict_of_tables
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
            indicator_name=ea2_code,
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
                indicator_name=ea2_code,
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
            ea2_dist_list = [[int(n) for n in v] for v in y["distribution"]]
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
            ea2_list = []
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            for year in years_to_evaluate:
                ea2_ = ea2(
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
                ea2_list.append(ea2_)
            # cache everything
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    "percentage": [ea2_["percentage"] for ea2_ in ea2_list],
                    "distribution": [ea2_["distribution"] for ea2_ in ea2_list]
                }
            )
            cache_json(
                indicator_name=ea2_code,
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
            ea2_dist_list = [l["distribution"] for l in ea2_list]
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea2_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea2_dist_list[i])
        plot = holoviews.Violin(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False,
            inner="quartiles",
            bandwidth=0.5,
            violin_color="#d3e3fd", 
            title=ea2_code + " - " + ea2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea2_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea2_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea2_dist_list[i], 75) - numpy.percentile(ea2_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea2_dist_list[i]) for i in range(len(years_to_evaluate))],
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
        disease_code = kwargs.get("disease_code", "_depression_")
        cohort_code = kwargs.get("cohort_code", "_a_")
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code=disease_code,
                cohort_code=cohort_code,
                indicator_widget_value=self.widgets_instance.param.value,
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
#

ea2_tab_names_langdict["en"].append("Help")
ea2_tab_names_langdict["it"].append("Aiuto")
ea2_tab_names_langdict["fr"].append("Aide")
ea2_tab_names_langdict["de"].append("Hilfe")
ea2_tab_names_langdict["es"].append("Ayuda")
ea2_tab_names_langdict["pt"].append("Ajuda")


class ea2_tab3(object):
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
                    The indicator is calculated as the percentage of patients having at least one outpatient community contact of type PSYCHOSOCIAL INTERVENTION (code "04")
                    in the year of inclusion.
                    The denominator is the number of patients that satisfy the variuos stratification parameters, 
                    and the numerator is the number of patients with at least one intervention in the year that are included in
                    the set of patients used to compute the denominator.
                    It takes into account various 
                    demographic factors such as year of inclusion, age, gender, civil status, 
                    job condition, and educational level.
                    </p>

                    <h3 style='{h3_style}'>Indicator Display</h3>
                    <p style='{p_style}'>
                    The indicator is displayed as a plot showing the percentage of patients having at least one
                    outpatient community contact over the years of data availability. The x-axis represents the years,
                    and the y-axis represents the percentage of patients. 
                    The plot is stratified by disease, allowing you to select a specific disease 
                    to view its treated prevalence over time.
                    The indicator is also displayed as a boxplot and a violin plot showing the distribution
                    of the number of interventions per patient, provided that the patient has at least one intervention
                    in the year.
                    </p>
                """,
            "it":
                f"""
                    <h3 style='{h3_style}'>Calcolo dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è calcolato come la percentuale di pazienti che hanno almeno un contatto ambulatoriale di tipo INTERVENTO PSICOSOCIALE (codice "04")
                    nell'anno di inclusione.
                    Il denominatore è il numero di pazienti che soddisfano i vari parametri di stratificazione, 
                    e il numeratore è il numero di pazienti con almeno un intervento nell'anno che sono inclusi nel
                    insieme di pazienti utilizzato per calcolare il denominatore.
                    Tiene conto di vari fattori demografici come l'anno di inclusione, l'età, il genere, lo stato civile, 
                    la condizione lavorativa e il livello di istruzione.
                    </p>

                    <h3 style='{h3_style}'>Visualizzazione dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è visualizzato come un grafico che mostra la percentuale di pazienti che hanno almeno un
                    contatto ambulatoriale con la comunità nel corso degli anni di disponibilità dei dati. L'asse x rappresenta gli anni,
                    e l'asse y rappresenta la percentuale di pazienti. 
                    Il grafico è stratificato per malattia, consentendoti di selezionare una malattia specifica 
                    per visualizzarne la prevalenza trattata nel tempo.
                    L'indicatore è anche visualizzato come un boxplot e un violino che mostrano la distribuzione
                    del numero di interventi per paziente, a condizione che il paziente abbia almeno un intervento
                    nell'anno.
                    </p>
                """,
            "fr":
                f"""
                    <h3 style='{h3_style}'>Calcul de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est calculé comme le pourcentage de patients ayant au moins un contact communautaire ambulatoire de type INTERVENTION PSYCHOSOCIALE (code "04")
                    dans l'année d'inclusion.
                    Le dénominateur est le nombre de patients qui satisfont aux différents paramètres de stratification, 
                    et le numérateur est le nombre de patients ayant au moins un intervention dans l'année qui sont inclus dans
                    l'ensemble des patients utilisés pour calculer le dénominateur.
                    Il tient compte de divers facteurs démographiques tels que l'année d'inclusion, l'âge, le sexe, l'état civil, 
                    la condition d'emploi et le niveau d'éducation.
                    </p>

                    <h3 style='{h3_style}'>Affichage de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est affiché sous forme de graphique montrant le pourcentage de patients ayant au moins un
                    contact communautaire ambulatoire au fil des années de disponibilité des données. L'axe x représente les années,
                    et l'axe y représente le pourcentage de patients. 
                    Le graphique est stratifié par maladie, vous permettant de sélectionner une maladie spécifique 
                    pour visualiser sa prévalence traitée au fil du temps.
                    L'indicateur est également affiché sous forme de boxplot et de violon montrant la distribution
                    du nombre d'interventions par patient, à condition que le patient ait au moins un intervention
                    dans l'année.
                    </p>
                """,
            "de":
                f"""
                    <h3 style='{h3_style}'>Indikatorberechnung</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Prozentsatz der Patienten berechnet, die mindestens einen ambulanten Gemeindekontakt vom Typ PSYCHOSOZIALER EINGRIFF (Code "04") haben
                    im Jahr der Aufnahme haben.
                    Der Nenner ist die Anzahl der Patienten, die die verschiedenen Stratifikationsparameter erfüllen, 
                    und der Zähler ist die Anzahl der Patienten mit mindestens einem Eingriff im Jahr, die in
                    die Gruppe der Patienten aufgenommen werden, die zur Berechnung des Nenners verwendet werden.
                    Er berücksichtigt verschiedene demografische Faktoren wie das Aufnahmejahr, das Alter, das Geschlecht, den Familienstand, 
                    die Beschäftigungssituation und das Bildungsniveau.
                    </p>

                    <h3 style='{h3_style}'>Anzeige des Indikators</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Diagramm dargestellt, das den Prozentsatz der Patienten zeigt, die mindestens einen
                    ambulanten Gemeindekontakt im Laufe der Jahre der Datenverfügbarkeit haben. Die x-Achse stellt die Jahre dar,
                    und die y-Achse stellt den Prozentsatz der Patienten dar. 
                    Das Diagramm ist nach Krankheit gegliedert, sodass Sie eine bestimmte Krankheit auswählen können, 
                    um ihre behandelte Prävalenz im Laufe der Zeit anzuzeigen.
                    Der Indikator wird auch als Boxplot und Violinplot dargestellt, die die Verteilung zeigen
                    der Anzahl der Eingriffe pro Patient, vorausgesetzt, der Patient hat mindestens einen Eingriff
                    im Jahr.
                    </p>
                """,
            "es":
                f"""
                    <h3 style='{h3_style}'>Cálculo del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se calcula como el porcentaje de pacientes que tienen al menos un contacto ambulatorio con la comunidad de tipo INTERVENCIÓN PSICOSOCIAL (código "04")
                    en el año de inclusión.
                    El denominador es el número de pacientes que satisfacen los diversos parámetros de estratificación, 
                    y el numerador es el número de pacientes con al menos un intervención en el año que están incluidos en
                    el conjunto de pacientes utilizados para calcular el denominador.
                    Tiene en cuenta varios factores demográficos como el año de inclusión, la edad, el género, el estado civil, 
                    la condición laboral y el nivel educativo.
                    </p>

                    <h3 style='{h3_style}'>Visualización del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se muestra como un gráfico que muestra el porcentaje de pacientes que tienen al menos un
                    contacto ambulatorio con la comunidad a lo largo de los años de disponibilidad de datos. El eje x representa los años,
                    y el eje y representa el porcentaje de pacientes. 
                    El gráfico está estratificado por enfermedad, lo que le permite seleccionar una enfermedad específica 
                    para ver su prevalencia tratada a lo largo del tiempo.
                    El indicador también se muestra como un boxplot y un violín que muestran la distribución
                    del número de intervenciones por paciente, siempre que el paciente tenga al menos un intervención
                    en el año.
                    </p>
                """,
            "pt":
                f"""
                    <h3 style='{h3_style}'>Cálculo do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é calculado como a percentagem de pacientes que têm pelo menos um contacto ambulatório com a comunidade do tipo INTERVENÇÃO PSICOSSOCIAL (código "04")
                    no ano de inclusão.
                    O denominador é o número de pacientes que satisfazem os vários parâmetros de estratificação, 
                    e o numerador é o número de pacientes com pelo menos uma intervenção no ano que estão incluídos em
                    o conjunto de pacientes utilizados para calcular o denominador.
                    Leva em consideração vários fatores demográficos como o ano de inclusão, a idade, o género, o estado civil, 
                    a condição de trabalho e o nível educacional.
                    </p>

                    <h3 style='{h3_style}'>Visualização do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é exibido como um gráfico que mostra a percentagem de pacientes que têm pelo menos um
                    contacto ambulatório com a comunidade ao longo dos anos de disponibilidade de dados. O eixo x representa os anos,
                    e o eixo y representa a percentagem de pacientes. 
                    O gráfico é estratificado por doença, permitindo-lhe selecionar uma doença específica 
                    para ver a sua prevalência tratada ao longo do tempo.
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
