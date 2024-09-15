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
from ...loading.loading import increase_loading_counter, decrease_loading_counter





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
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    type_int_list = [1, 2, 3, 4, 5, 6, 7, 9]
    out_dict_key_list = type_int_list+["any_type"]
    mb2 = {k: [0] for k in out_dict_key_list}
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
        WHERE 
            ID_SUBJECT IN (
                /* Must be in the right stratification */
                SELECT DISTINCT ID_SUBJECT FROM {stratified_demographics_table_name}
                INTERSECT
                /* Must have the disease at the year of inclusion (prevalent patient) */
                SELECT DISTINCT ID_SUBJECT FROM cohorts WHERE 
                    YEAR_OF_ONSET <= {year_of_inclusion}
                    AND 
                    ID_DISORDER = '{disease_db_code}'
            )
            /* Here, TYPE_INT can be any but NULL */
            AND
            TYPE_INT IS NOT NULL
            /* DT_INT year must be in the year of inclusion */
            AND
            CAST(strftime('%Y', DT_INT) AS INTEGER) = {year_of_inclusion}
        GROUP BY ID_SUBJECT
    """)
    mb2["any_type"] = [int(c[0]) for c in cursor.fetchall()]
    if sum(mb2["any_type"]) == 0:
        mb2["any_type"] = [0]
        return mb2
    # first version: outer while loop
    for type_int_code in type_int_list:
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM interventions
            WHERE 
                ID_SUBJECT IN (
                    /* Must be in the right stratification */
                    SELECT DISTINCT ID_SUBJECT FROM {stratified_demographics_table_name}
                    INTERSECT
                    /* Must have the disease at the year of inclusion (prevalent patient) */
                    SELECT DISTINCT ID_SUBJECT FROM cohorts WHERE 
                        YEAR_OF_ONSET <= {year_of_inclusion}
                        AND 
                        ID_DISORDER = '{disease_db_code}'
                )
                AND
                /* Here, TYPE_INT must be equal to type_int_code */
                TYPE_INT = {int(type_int_code)}
                AND
                /* DT_INT year must be in the year of inclusion */
                CAST(strftime('%Y', DT_INT) AS INTEGER) = {year_of_inclusion}
            GROUP BY ID_SUBJECT
        """)
        mb2[type_int_code] = [int(c[0]) for c in cursor.fetchall()]
    # delete the table of stratified demograpohics
    cursor.execute(f"DROP TABLE IF EXISTS {stratified_demographics_table_name}")
    # close the cursor
    cursor.close()
    # check output
    for k in mb2:
        if len(mb2[k]) == 0:
            mb2[k] = [0]
    # return
    return mb2
    

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
            y = {int(k) if k != "any_type" else k: y[k] for k in y}
            # get the values specific for this tab,
            # which are the sum of the interventions for each year
            # from list[list[int]] to list[int] spanning along the years of inclusion
            mb2_all = [sum(y["any_type"][i]) for i in range(len(y["any_type"]))]
            mb2_01 = [sum(y[1][i]) for i in range(len(y[1]))]
            mb2_02 = [sum(y[2][i]) for i in range(len(y[2]))]
            mb2_03 = [sum(y[3][i]) for i in range(len(y[3]))]
            mb2_04 = [sum(y[4][i]) for i in range(len(y[4]))]
            mb2_05 = [sum(y[5][i]) for i in range(len(y[5]))]
            mb2_06 = [sum(y[6][i]) for i in range(len(y[6]))]
            mb2_07 = [sum(y[7][i]) for i in range(len(y[7]))]
            mb2_other = [sum(y[9][i]) for i in range(len(y[9]))]
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
            cursor.close()
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            # get the indicator distribution of values (y-axis) for the years of inclusion (x-axis on the plot) for caching
            mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_09 = [], [], [], [], [], [], [], [], [] # these will be list of lists of integers
            for year in years_to_evaluate:
                mb2_ = mb2(
                    connection=self._db_conn,
                    cohorts_required=True,
                    disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                    year_of_inclusion=year,
                    age=age_interval_list,
                    gender=gender,
                    civil_status=civil_status,
                    job_condition=job_condition,
                    educational_level=educational_level
                )
                mb2_all.append(mb2_["any_type"])
                mb2_01.append(mb2_[1])
                mb2_02.append(mb2_[2])
                mb2_03.append(mb2_[3])
                mb2_04.append(mb2_[4])
                mb2_05.append(mb2_[5])
                mb2_06.append(mb2_[6])
                mb2_07.append(mb2_[7])
                mb2_09.append(mb2_[9])
            # cache the result:
            # a dict[int|str: list[list[int]]]
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    1 : mb2_01,
                    2 : mb2_02,
                    3 : mb2_03,
                    4 : mb2_04,
                    5 : mb2_05,
                    6 : mb2_06,
                    7 : mb2_07,
                    9 : mb2_09,
                    "any_type": mb2_all
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
            # now, get the values specific for this tab,
            # which are the sum of the interventions for each year
            # from list[list[int]] to list[int] spanning along the years of inclusion
            mb2_all = [sum(mb2_all[i]) for i in range(len(mb2_all))]
            mb2_01 = [sum(mb2_01[i]) for i in range(len(mb2_01))]
            mb2_02 = [sum(mb2_02[i]) for i in range(len(mb2_02))]
            mb2_03 = [sum(mb2_03[i]) for i in range(len(mb2_03))]
            mb2_04 = [sum(mb2_04[i]) for i in range(len(mb2_04))]
            mb2_05 = [sum(mb2_05[i]) for i in range(len(mb2_05))]
            mb2_06 = [sum(mb2_06[i]) for i in range(len(mb2_06))]
            mb2_07 = [sum(mb2_07[i]) for i in range(len(mb2_07))]
            mb2_other = [sum(mb2_09[i]) for i in range(len(mb2_09))]
        # plot - use bokeh because it allows independent zooming
        _y_max_plot = max([max(mb2_all), 1/1.15])
        _y_max_plot *= 1.15
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_year_langdict[language_code], "@x"),
                (_y_axis_langdict_all[language_code], "@y")
            ]
        )
        plot = bokeh.plotting.figure(
            sizing_mode="stretch_width",
            height=350,
            title=mb2_code + " - " + mb2_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code],
            x_axis_label=_year_langdict[language_code],
            x_range=(years_to_evaluate[0]-0.5, years_to_evaluate[-1]+0.5),
            y_axis_label=_y_axis_langdict_all[language_code],
            y_range=(0, _y_max_plot),
            tools="pan,wheel_zoom,box_zoom,reset,save",
            toolbar_location="right",
        )
        plot.xaxis.ticker = numpy.sort(years_to_evaluate)
        plot.xgrid.grid_line_color = None
        for name_, n_list in zip(
            ["All", 1, 2, 3, 4, 5, 6, 7, 9],
            [mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other]
        ):
            plot.line(
                x=years_to_evaluate, 
                y=n_list,
                legend_label=f"{name_}: " + str(_all_interventions_langdict[language_code] if name_ == "All" else INTERVENTIONS_CODES_LANGDICT_MAP[language_code][name_]["legend"]),
                line_color=INTERVENTIONS_CODES_COLOR_DICT[name_]
            )
            plot.circle(
                x=years_to_evaluate, 
                y=n_list,
                legend_label=f"{name_}: " + str(_all_interventions_langdict[language_code] if name_ == "All" else INTERVENTIONS_CODES_LANGDICT_MAP[language_code][name_]["legend"]),
                fill_color=INTERVENTIONS_CODES_COLOR_DICT[name_],
                line_width=0,
                size=10
            )
        plot.add_tools(hover_tool)
        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        toggle_legend_js = bokeh.models.CustomJS(
            args=dict(leg=plot.legend[0]), 
            code="""
                    if (leg.visible) {
                        leg.visible = false
                        }
                    else {
                        leg.visible = true
                    }
                """
            )
        plot.js_on_event(bokeh.events.DoubleTap, toggle_legend_js)
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

mb2_tab_names_langdict["en"].append("Indicator distribution boxplot")
mb2_tab_names_langdict["it"].append("Distribuzione dell'indicatore con boxplot")
mb2_tab_names_langdict["fr"].append("Distribution de l'indicateur avec boxplot")
mb2_tab_names_langdict["de"].append("Indikatorverteilung Boxplot")
mb2_tab_names_langdict["es"].append("Distribución del indicador con boxplot")
mb2_tab_names_langdict["pt"].append("Distribuição do indicador com boxplot")

class mb2_tab1(object):
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
            y = {int(k) if k != "any_type" else k: y[k] for k in y}
            # get the values specific for this tab,
            mb2_all = y["any_type"]
            mb2_01 = y[1]
            mb2_02 = y[2]
            mb2_03 = y[3]
            mb2_04 = y[4]
            mb2_05 = y[5]
            mb2_06 = y[6]
            mb2_07 = y[7]
            mb2_other = y[9]
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
            cursor.close()
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            # get the indicator distribution of values (y-axis) for the years of inclusion (x-axis on the plot) for caching
            mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_09 = [], [], [], [], [], [], [], [], [] # these will be list of lists of integers
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
                mb2_all.append(mb2_["any_type"])
                mb2_01.append(mb2_[1])
                mb2_02.append(mb2_[2])
                mb2_03.append(mb2_[3])
                mb2_04.append(mb2_[4])
                mb2_05.append(mb2_[5])
                mb2_06.append(mb2_[6])
                mb2_07.append(mb2_[7])
                mb2_09.append(mb2_[9])
            # cache the result:
            # a dict[int|str: list[list[int]]]
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    1 : mb2_01,
                    2 : mb2_02,
                    3 : mb2_03,
                    4 : mb2_04,
                    5 : mb2_05,
                    6 : mb2_06,
                    7 : mb2_07,
                    9 : mb2_09,
                    "any_type": mb2_all
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
            # now, get the values specific for this tab,
            # already fine, just 09 -> other
            mb2_other = mb2_09
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        c_ = []
        v_ = []
        results_list = [mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other]
        for i, y_ in enumerate(years_to_evaluate):
            for j, type_int in enumerate(INTERVENTIONS_CODES_COLOR_DICT.keys()):
                n = len(results_list[j][i])
                g_.extend([y_] * n)
                c_.extend([type_int] * n)
                v_.extend(results_list[j][i])
        plot = holoviews.BoxWhisker(
            (g_, c_, v_), 
            kdims=[("year", _year_langdict[language_code]), ("tyep_int", _intervention_type_code_langdict[language_code])], 
            vdims=[("dist", _y_axis_langdict[language_code])]
        ).opts(
            show_legend=False, 
            box_fill_color="#d3e3fd", 
            title=mb2_code + " - " + mb2_name_langdict[language_code] + DISEASES_LANGDICT[language_code][disease_code],
        )
        bokeh_plot = holoviews.render(plot)
        bokeh_plot.sizing_mode="stretch_width"
        bokeh_plot.height=350
        bokeh_plot.toolbar.autohide = True
        bokeh_plot.toolbar.logo = None
        # add a transparent Circle plot to show some info with a custom hover tool
        x_source = []
        year_source = []
        int_type_source = []
        total_source = []
        median_source = []
        mean_source = []
        stdev_source = []
        q1_source = []
        q3_source = []
        iqr_source = []
        i = 0
        for i_y_, y_ in enumerate(years_to_evaluate):
            for type_int_ in [ "All", 1, 2, 3, 4, 5, 6, 7, 9]:
                # position in plot
                x_source.append(
                    0.5 + i + 1.4*(i // len(INTERVENTIONS_CODES_COLOR_DICT.keys()))
                )
                i += 1
                # hover data
                year_source.append(y_)
                if type_int_ == "All":
                    int_type_source.append(
                        _all_interventions_langdict[language_code]
                    )
                else:
                    int_type_source.append(
                        INTERVENTIONS_CODES_LANGDICT_MAP[language_code][type_int_]["short"]
                    )
                d_src = None
                if type_int_ == "All":
                    d_src = mb2_all[i_y_]
                elif type_int_ == 1:
                    d_src = mb2_01[i_y_]
                elif type_int_ == 2:
                    d_src = mb2_02[i_y_]
                elif type_int_ == 3:
                    d_src = mb2_03[i_y_]
                elif type_int_ == 4:
                    d_src = mb2_04[i_y_]
                elif type_int_ == 5:
                    d_src = mb2_05[i_y_]
                elif type_int_ == 6:
                    d_src = mb2_06[i_y_]
                elif type_int_ == 7:
                    d_src = mb2_07[i_y_]
                elif type_int_ == 9:
                    d_src = mb2_other[i_y_]
                total_source.append(len(d_src))
                median_source.append(numpy.median(d_src))
                mean_source.append(numpy.mean(d_src))
                stdev_source.append(numpy.std(d_src))
                q1_source.append(numpy.percentile(d_src, 25))
                q3_source.append(numpy.percentile(d_src, 75))
                iqr_source.append(q3_source[-1] - q1_source[-1])
        source = bokeh.models.ColumnDataSource({
            "x": x_source,
            "year": year_source,
            "type_int": int_type_source,
            "count": total_source,
            "mean": mean_source,
            "median": median_source,
            "stdev": stdev_source,
            "q1": q1_source,
            "q3": q3_source,
            "iqr": iqr_source
        })
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_hover_tool_langdict[language_code]["year"], "@year"),
                (_hover_tool_langdict[language_code]["intervention_type"], "@type_int"),
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
            x="x", 
            source=source,
            line_width=5,
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
    
#
    

mb2_tab_names_langdict["en"].append("Indicator distribution violin plot")
mb2_tab_names_langdict["it"].append("Distribuzione dell'indicatore con violino")
mb2_tab_names_langdict["fr"].append("Distribution de l'indicateur avec violon")
mb2_tab_names_langdict["de"].append("Indikatorverteilung Geigenplot")
mb2_tab_names_langdict["es"].append("Distribución del indicador con violín")
mb2_tab_names_langdict["pt"].append("Distribuição do indicador com violino")

class mb2_tab2(object):
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
            y = {int(k) if k != "any_type" else k: y[k] for k in y}
            # get the values specific for this tab,
            mb2_all = y["any_type"]
            mb2_01 = y[1]
            mb2_02 = y[2]
            mb2_03 = y[3]
            mb2_04 = y[4]
            mb2_05 = y[5]
            mb2_06 = y[6]
            mb2_07 = y[7]
            mb2_other = y[9]
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
            cursor.close()
            years_to_evaluate = [y for y in range(min_year_, time.localtime().tm_year+1)]
            # get the indicator distribution of values (y-axis) for the years of inclusion (x-axis on the plot) for caching
            mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_09 = [], [], [], [], [], [], [], [], [] # these will be list of lists of integers
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
                mb2_all.append(mb2_["any_type"])
                mb2_01.append(mb2_[1])
                mb2_02.append(mb2_[2])
                mb2_03.append(mb2_[3])
                mb2_04.append(mb2_[4])
                mb2_05.append(mb2_[5])
                mb2_06.append(mb2_[6])
                mb2_07.append(mb2_[7])
                mb2_09.append(mb2_[9])
            # cache the result:
            # a dict[int|str: list[list[int]]]
            x_json = json.dumps(years_to_evaluate)
            y_json = json.dumps(
                {
                    1 : mb2_01,
                    2 : mb2_02,
                    3 : mb2_03,
                    4 : mb2_04,
                    5 : mb2_05,
                    6 : mb2_06,
                    7 : mb2_07,
                    9 : mb2_09,
                    "any_type": mb2_all
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
            # now, get the values specific for this tab,
            # already fine, just 09 -> other
            mb2_other = mb2_09
        # plot: BoxWhisker
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        c_ = []
        v_ = []
        results_list = [mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other]
        for i, y_ in enumerate(years_to_evaluate):
            for j, type_int in enumerate(INTERVENTIONS_CODES_COLOR_DICT.keys()):
                n = len(results_list[j][i])
                g_.extend([y_] * n)
                c_.extend([type_int] * n)
                v_.extend(results_list[j][i])
        plot = holoviews.Violin(
            (g_, c_, v_), 
            kdims=[("year", _year_langdict[language_code]), ("tyep_int", _intervention_type_code_langdict[language_code])], 
            vdims=[("dist", _y_axis_langdict[language_code])]
        ).sort().opts(
            show_legend=False,
            inner="quartiles",
            bandwidth=1.5,
            violin_color="#d3e3fd",
            title=mb2_code + " - " + mb2_name_langdict[language_code] + DISEASES_LANGDICT[language_code][disease_code],
        )
        bokeh_plot = holoviews.render(plot)
        bokeh_plot.sizing_mode="stretch_width"
        bokeh_plot.height=350
        bokeh_plot.toolbar.autohide = True
        bokeh_plot.toolbar.logo = None
        # add a transparent Circle plot to show some info with a custom hover tool
        x_source = []
        year_source = []
        int_type_source = []
        total_source = []
        median_source = []
        mean_source = []
        stdev_source = []
        q1_source = []
        q3_source = []
        iqr_source = []
        i = 0
        for i_y_, y_ in enumerate(years_to_evaluate):
            for type_int_ in ["All", 1, 2, 3, 4, 5, 6, 7, 9]:
                # position in plot
                x_source.append(
                    0.5 + i + 1.4*(i // len(INTERVENTIONS_CODES_COLOR_DICT.keys()))
                )
                i += 1
                # hover data
                year_source.append(y_)
                if type_int_ == "All":
                    int_type_source.append(
                        _all_interventions_langdict[language_code]
                    )
                else:
                    int_type_source.append(
                        INTERVENTIONS_CODES_LANGDICT_MAP[language_code][type_int_]["short"]
                    )
                d_src = None
                if type_int_ == "All":
                    d_src = mb2_all[i_y_]
                elif type_int_ == 1:
                    d_src = mb2_01[i_y_]
                elif type_int_ == 2:
                    d_src = mb2_02[i_y_]
                elif type_int_ == 3:
                    d_src = mb2_03[i_y_]
                elif type_int_ == 4:
                    d_src = mb2_04[i_y_]
                elif type_int_ == 5:
                    d_src = mb2_05[i_y_]
                elif type_int_ == 6:
                    d_src = mb2_06[i_y_]
                elif type_int_ == 7:
                    d_src = mb2_07[i_y_]
                elif type_int_ == 9:
                    d_src = mb2_other[i_y_]
                else:
                    print("Type int: ", type_int_)
                total_source.append(len(d_src))
                median_source.append(numpy.median(d_src))
                mean_source.append(numpy.mean(d_src))
                stdev_source.append(numpy.std(d_src))
                q1_source.append(numpy.percentile(d_src, 25))
                q3_source.append(numpy.percentile(d_src, 75))
                iqr_source.append(q3_source[-1] - q1_source[-1])
        source = bokeh.models.ColumnDataSource({
            "x": x_source,
            "year": year_source,
            "type_int": int_type_source,
            "count": total_source,
            "mean": mean_source,
            "median": median_source,
            "stdev": stdev_source,
            "q1": q1_source,
            "q3": q3_source,
            "iqr": iqr_source
        })
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_hover_tool_langdict[language_code]["year"], "@year"),
                (_hover_tool_langdict[language_code]["intervention_type"], "@type_int"),
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
            x="x", 
            source=source,
            line_width=5,
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
        

#

mb2_tab_names_langdict["en"].append("Help")
mb2_tab_names_langdict["it"].append("Aiuto")
mb2_tab_names_langdict["fr"].append("Aide")
mb2_tab_names_langdict["de"].append("Hilfe")
mb2_tab_names_langdict["es"].append("Ayuda")
mb2_tab_names_langdict["pt"].append("Ajuda")


class mb2_tab3(object):
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
                    <h3 style='{h3_style}'>Types of Intervention</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Indicator Calculation</h3>
                    <p style='{p_style}'>
                    The indicator is calculated as the number of interventions delivered by Mental Health Outpatient Facilities
                    by type of interventions. The indicator is itself stratified by year
                    and by type of intervention, and is calculated for each year of data availability.
                    It takes into account various demographic factors such as age, gender, civil status, 
                    job condition, and educational level.
                    </p>

                    <h3 style='{h3_style}'>Indicator Display</h3>
                    <p style='{p_style}'>
                    The indicator is displayed in three different ways: as a line plot, as a boxplot, and as a violin plot.<br>
                    The line plot shows the total number of interventions delivered by Mental Health Outpatient Facilities
                    by type of interventions, stratified by year. Double-click on the legend area to toggle its visibility.<br>
                    The boxplot shows the distribution summary of the number of interventions delivered by Mental Health Outpatient Facilities
                    by type of interventions, stratified by year.<br>
                    The violin plot shows the detailed distribution of the number of interventions delivered by Mental Health Outpatient Facilities
                    by type of interventions, stratified by year.
                    </p>
                """,
            "it":
                f"""
                    <h3 style='{h3_style}'>Tipi di Intervento</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Calcolo dell'Indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è calcolato come il numero di interventi erogati dalle strutture di salute mentale ambulatoriali
                    per tipo di interventi. L'indicatore è a sua volta stratificato per anno
                    e per tipo di intervento, ed è calcolato per ciascun anno di disponibilità dei dati.
                    Considera vari fattori demografici come età, genere, stato civile,
                    condizione lavorativa e livello di istruzione.
                    </p>

                    <h3 style='{h3_style}'>Visualizzazione dell'Indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è visualizzato in tre modi diversi: come grafico a linee, come boxplot e come violino.<br>
                    Il grafico a linee mostra il numero totale di interventi erogati dalle strutture di salute mentale ambulatoriali
                    per tipo di interventi, stratificati per anno. Fare doppio clic sull'area della legenda per attivare/disattivare la sua visibilità.<br>
                    Il boxplot mostra il riepilogo della distribuzione del numero di interventi erogati dalle strutture di salute mentale ambulatoriali
                    per tipo di interventi, stratificati per anno.<br>
                    Il violino mostra la distribuzione dettagliata del numero di interventi erogati dalle strutture di salute mentale ambulatoriali
                    per tipo di interventi, stratificati per anno.
                    </p>
                """,
            "fr":
                f"""
                    <h3 style='{h3_style}'>Types d'Intervention</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Calcul de l'Indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est calculé comme le nombre d'interventions dispensées par les établissements de santé mentale ambulatoires
                    par type d'interventions. L'indicateur est lui-même stratifié par année
                    et par type d'intervention, et est calculé pour chaque année de disponibilité des données.
                    Il prend en compte divers facteurs démographiques tels que l'âge, le sexe, l'état civil,
                    la condition d'emploi et le niveau d'éducation.
                    </p>

                    <h3 style='{h3_style}'>Affichage de l'Indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est affiché de trois manières différentes : sous forme de graphique linéaire, de boîte à moustaches et de violon.<br>
                    Le graphique linéaire montre le nombre total d'interventions dispensées par les établissements de santé mentale ambulatoires
                    par type d'interventions, stratifié par année. Double-cliquez sur la zone de la légende pour basculer sa visibilité.<br>
                    Le boxplot montre le résumé de la distribution du nombre d'interventions dispensées par les établissements de santé mentale ambulatoires
                    par type d'interventions, stratifié par année.<br>
                    Le violon montre la distribution détaillée du nombre d'interventions dispensées par les établissements de santé mentale ambulatoires
                    par type d'interventions, stratifié par année.
                    </p>
                """,
            "de":
                f"""
                    <h3 style='{h3_style}'>Arten von Interventionen</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Indikatorberechnung</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als die Anzahl der Interventionen berechnet, die von ambulanten Einrichtungen für psychische Gesundheit durchgeführt wurden
                    nach Art der Interventionen. Der Indikator ist selbst nach Jahr stratifiziert
                    und nach Art der Intervention, und wird für jedes Jahr der Datenverfügbarkeit berechnet.
                    Er berücksichtigt verschiedene demografische Faktoren wie Alter, Geschlecht, Familienstand,
                    Beschäftigungsstatus und Bildungsniveau.
                    </p>

                    <h3 style='{h3_style}'>Indikatoranzeige</h3>
                    <p style='{p_style}'>
                    Der Indikator wird auf drei verschiedene Arten angezeigt: als Liniendiagramm, als Boxplot und als Violinplot.<br>
                    Das Liniendiagramm zeigt die Gesamtzahl der Interventionen, die von ambulanten Einrichtungen für psychische Gesundheit durchgeführt wurden
                    nach Art der Interventionen, stratifiziert nach Jahr. Doppelklicken Sie auf den Legendenbereich, um dessen Sichtbarkeit zu wechseln.<br>
                    Der Boxplot zeigt die Zusammenfassung der Verteilung der Anzahl der Interventionen, die von ambulanten Einrichtungen für psychische Gesundheit durchgeführt wurden
                    nach Art der Interventionen, stratifiziert nach Jahr.<br>
                    Das Violinplot zeigt die detaillierte Verteilung der Anzahl der Interventionen, die von ambulanten Einrichtungen für psychische Gesundheit durchgeführt wurden
                    nach Art der Interventionen, stratifiziert nach Jahr.
                    </p>
                """,
            "es":
                f"""
                    <h3 style='{h3_style}'>Tipos de Intervención</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Cálculo del Indicador</h3>
                    <p style='{p_style}'>
                    El indicador se calcula como el número de intervenciones realizadas por los centros de salud mental ambulatorios
                    por tipo de intervenciones. El indicador está estratificado por año
                    y por tipo de intervención, y se calcula para cada año de disponibilidad de datos.
                    Toma en cuenta varios factores demográficos como la edad, el género, el estado civil,
                    la condición laboral y el nivel educativo.
                    </p>

                    <h3 style='{h3_style}'>Visualización del Indicador</h3>
                    <p style='{p_style}'>
                    El indicador se muestra de tres formas diferentes: como un gráfico de líneas, como un boxplot y como un violín.<br>
                    El gráfico de líneas muestra el número total de intervenciones realizadas por los centros de salud mental ambulatorios
                    por tipo de intervenciones, estratificado por año. Haga doble clic en el área de la leyenda para cambiar su visibilidad.<br>
                    El boxplot muestra el resumen de la distribución del número de intervenciones realizadas por los centros de salud mental ambulatorios
                    por tipo de intervenciones, estratificado por año.<br>
                    El violín muestra la distribución detallada del número de intervenciones realizadas por los centros de salud mental ambulatorios
                    por tipo de intervenciones, estratificado por año.
                    </p>
                """,
            "pt":
                f"""
                    <h3 style='{h3_style}'>Tipos de Intervenção</h3>
                    <p style='{p_style}'>
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][1]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][1]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][2]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][2]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][3]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][3]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][4]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][4]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][5]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][5]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][6]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][6]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][7]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][7]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"][9]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"][9]["long"]}<br>
                    </p>
                    
                    <h3 style='{h3_style}'>Cálculo do Indicador</h3>
                    <p style='{p_style}'>
                    O indicador é calculado como o número de intervenções realizadas pelos centros de saúde mental ambulatorial
                    por tipo de intervenções. O indicador é ele mesmo estratificado por ano
                    e por tipo de intervenção, e é calculado para cada ano de disponibilidade de dados.
                    Leva em consideração vários fatores demográficos como idade, gênero, estado civil,
                    condição de trabalho e nível educacional.
                    </p>

                    <h3 style='{h3_style}'>Visualização do Indicador</h3>
                    <p style='{p_style}'>
                    O indicador é exibido de três maneiras diferentes: como um gráfico de linhas, como um boxplot e como um violino.<br>
                    O gráfico de linhas mostra o número total de intervenções realizadas pelos centros de saúde mental ambulatorial
                    por tipo de intervenções, estratificado por ano. Dê um duplo clique na área da legenda para alternar sua visibilidade.<br>
                    O boxplot mostra o resumo da distribuição do número de intervenções realizadas pelos centros de saúde mental ambulatorial
                    por tipo de intervenções, estratificado por ano.<br>
                    O violino mostra a distribuição detalhada do número de intervenções realizadas pelos centros de saúde mental ambulatorial
                    por tipo de intervenções, estratificado por ano.
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
                },
                stylesheets=[
                    """
                    .dot {
                        height: 0.9em;
                        width: 0.9em;
                        border-radius: 50%;
                        display: inline-block;
                        margin-bottom: -0.1em;
                        margin-right: 0.4em;
                    }
                    .c01 { background-color: %s; }
                    .c02 { background-color: %s; }
                    .c03 { background-color: %s; }
                    .c04 { background-color: %s; }
                    .c05 { background-color: %s; }
                    .c06 { background-color: %s; }
                    .c07 { background-color: %s; }
                    .Other { background-color: %s; }
                    """
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[1], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[2], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[3], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[4], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[5], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[6], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[7], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT[9], 1)
                ]
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