import numpy
import pandas
import panel
from ..._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)
import holoviews
holoviews.extension('bokeh') #################################################################

import bokeh.palettes
import bokeh.models
import bokeh.events
import bokeh.plotting

from ...database.database import DISEASE_CODE_TO_DB_CODE
from ..logic_utilities import clean_indicator_getter_input, stratify_demographics
from ..widget import indicator_widgets
from ...main_selectors.disease_text import DS_TITLE as DISEASES_LANGDICT


# indicator logic
def mb2(**kwargs):
    """
    output:
    dict[str: list[int]]
    keys level 0: ["01", "02", "03", "04", "05", "06", "07", "Other"] # TYPE_INT levels
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    tables = kwargs.get("dict_of_tables", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    type_int_list = ["01", "02", "03", "04", "05", "06", "07", "Other"]
    mb2 = {
        k: None for k in type_int_list
    }
    # logic
    # - first find stratified demographics
    valid_patient_ids = stratify_demographics(
        tables["demographics"],
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    # stratify patients by disease: from valid_patient_ids, select only the ones that in the cohorts
    # table have at least one entry for the desired disease
    ids_with_disease: numpy.ndarray = tables["cohorts"].loc[
        (tables["cohorts"][disease_db_code] == "Y") & (tables["cohorts"]["YEAR_ENTRY"] <= year_of_inclusion),
        "ID_SUBJECT"
    ].unique()
    valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_with_disease)]
    # patients are stratified, now we have to check in the interventions table
    # for each row (representing a sanitary intervention) if the patient is in the list and how many times
    # the intervention is repeated
    for type_int in type_int_list:
        # get the rows of the interventions table that are compatible with the stratification parameters
        condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
        condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
        condition = condition & (tables["interventions"]["TYPE_INT"] == type_int)
        condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
        # get the number of interventions
        if condition.sum() > 0:
            # get the distribution of the number of interventions
            val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
            mb2[type_int] = val_counts.to_list()
        else:
            mb2[type_int] = [0]
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
    def __init__(self, dict_of_tables: dict):
        self._language_code = "en"
        self._dict_of_tables = dict_of_tables
        self.widgets_instance = indicator_widgets(
             language_code=self._language_code,
        )
        # pane row
        self._pane_styles = {
        }
        self._pane_stylesheet = ""

    def get_plot(self, **kwargs):
        # inputs
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other = [], [], [], [], [], [], [], [], []
        for year in years_to_evaluate:
            mb2_ = mb2(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            mb2_all.append(
                numpy.sum(
                    mb2_["01"] + mb2_["02"] + mb2_["03"] + mb2_["04"] + mb2_["05"] + mb2_["06"] + mb2_["07"] + mb2_["Other"]
                )
            )
            mb2_01.append(numpy.sum(mb2_["01"]))
            mb2_02.append(numpy.sum(mb2_["02"]))
            mb2_03.append(numpy.sum(mb2_["03"]))
            mb2_04.append(numpy.sum(mb2_["04"]))
            mb2_05.append(numpy.sum(mb2_["05"]))
            mb2_06.append(numpy.sum(mb2_["06"]))
            mb2_07.append(numpy.sum(mb2_["07"]))
            mb2_other.append(numpy.sum(mb2_["Other"]))
        # plot - use bokeh because it allows independent zooming
        _y_max_plot = max(mb2_all)
        _y_max_plot *= 1.15
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_year_langdict[language_code], "@x"),
                (_y_axis_langdict_all[language_code], "@y")
            ]
        )
        plot = bokeh.plotting.figure(
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
            ["All", "01", "02", "03", "04", "05", "06", "07", "Other"],
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
        out = panel.pane.Bokeh(plot)
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
                age_temp_1=self.widgets_instance.widget_age_instance.widget_age_all,
                age_temp_2=self.widgets_instance.widget_age_instance.widget_age_lower,
                age_temp_3=self.widgets_instance.widget_age_instance.widget_age_upper,
                age_temp_4=self.widgets_instance.widget_age_instance.widget_age_value,
                gender=self.widgets_instance.widget_gender,
                civil_status=self.widgets_instance.widget_civil_status,
                job_condition=self.widgets_instance.widget_job_condition,
                educational_level=self.widgets_instance.widget_educational_level
            ),
            self.widgets_instance.get_panel(language_code=language_code),
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
        
#

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
        self.widgets_instance = indicator_widgets(
             language_code=self._language_code,
        )
        # pane row
        self._pane_styles = {
        }
        self._pane_stylesheet = ""

    def get_plot(self, **kwargs):
        # inputs
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other = [], [], [], [], [], [], [], [], []
        for year in years_to_evaluate:
            mb2_ = mb2(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            mb2_all.append(
                    mb2_["01"] + mb2_["02"] + mb2_["03"] + mb2_["04"] + mb2_["05"] + mb2_["06"] + mb2_["07"] + mb2_["Other"]
            )
            mb2_01.append(mb2_["01"])
            mb2_02.append(mb2_["02"])
            mb2_03.append(mb2_["03"])
            mb2_04.append(mb2_["04"])
            mb2_05.append(mb2_["05"])
            mb2_06.append(mb2_["06"])
            mb2_07.append(mb2_["07"])
            mb2_other.append(mb2_["Other"])
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
            title=mb2_code + " - " + mb2_name_langdict[language_code] + " (distributions) - " + DISEASES_LANGDICT[language_code][disease_code],
        )
        return panel.pane.HoloViews(plot)
        
    

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
                age_temp_1=self.widgets_instance.widget_age_instance.widget_age_all,
                age_temp_2=self.widgets_instance.widget_age_instance.widget_age_lower,
                age_temp_3=self.widgets_instance.widget_age_instance.widget_age_upper,
                age_temp_4=self.widgets_instance.widget_age_instance.widget_age_value,
                gender=self.widgets_instance.widget_gender,
                civil_status=self.widgets_instance.widget_civil_status,
                job_condition=self.widgets_instance.widget_job_condition,
                educational_level=self.widgets_instance.widget_educational_level
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
        self.widgets_instance = indicator_widgets(
             language_code=self._language_code,
        )
        # pane row
        self._pane_styles = {
        }
        self._pane_stylesheet = ""

    def get_plot(self, **kwargs):
        # inputs
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        mb2_all, mb2_01, mb2_02, mb2_03, mb2_04, mb2_05, mb2_06, mb2_07, mb2_other = [], [], [], [], [], [], [], [], []
        for year in years_to_evaluate:
            mb2_ = mb2(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            mb2_all.append(
                    mb2_["01"] + mb2_["02"] + mb2_["03"] + mb2_["04"] + mb2_["05"] + mb2_["06"] + mb2_["07"] + mb2_["Other"]
            )
            mb2_01.append(mb2_["01"])
            mb2_02.append(mb2_["02"])
            mb2_03.append(mb2_["03"])
            mb2_04.append(mb2_["04"])
            mb2_05.append(mb2_["05"])
            mb2_06.append(mb2_["06"])
            mb2_07.append(mb2_["07"])
            mb2_other.append(mb2_["Other"])
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
        ).opts(
            title=mb2_code + " - " + mb2_name_langdict[language_code] + " (distributions) - " + DISEASES_LANGDICT[language_code][disease_code],
        )
        return panel.pane.HoloViews(plot)
    
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
                age_temp_1=self.widgets_instance.widget_age_instance.widget_age_all,
                age_temp_2=self.widgets_instance.widget_age_instance.widget_age_lower,
                age_temp_3=self.widgets_instance.widget_age_instance.widget_age_upper,
                age_temp_4=self.widgets_instance.widget_age_instance.widget_age_value,
                gender=self.widgets_instance.widget_gender,
                civil_status=self.widgets_instance.widget_civil_status,
                job_condition=self.widgets_instance.widget_job_condition,
                educational_level=self.widgets_instance.widget_educational_level
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["en"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["en"]["Other"]["long"]}<br>
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["it"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["it"]["Other"]["long"]}<br>
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["fr"]["Other"]["long"]}<br>
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["de"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["de"]["Other"]["long"]}<br>
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["es"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["es"]["Other"]["long"]}<br>
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
                    <span class="dot c01"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["01"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["01"]["long"]}<br>
                    <span class="dot c02"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["02"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["02"]["long"]}<br>
                    <span class="dot c03"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["03"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["03"]["long"]}<br>
                    <span class="dot c04"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["04"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["04"]["long"]}<br>
                    <span class="dot c05"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["05"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["05"]["long"]}<br>
                    <span class="dot c06"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["06"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["06"]["long"]}<br>
                    <span class="dot c07"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["07"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["07"]["long"]}<br>
                    <span class="dot Other"></span><b>{INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["Other"]["short"]}</b>: {INTERVENTIONS_CODES_LANGDICT_MAP["pt"]["Other"]["long"]}<br>
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
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["01"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["02"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["03"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["04"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["05"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["06"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["07"], 1)
                    .replace("%s", INTERVENTIONS_CODES_COLOR_DICT["Other"], 1)
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


    from ...database.database import FILES_FOLDER, DATABASE_FILENAMES_DICT, read_databases, preprocess_demographics_database, preprocess_interventions_database, preprocess_cohorts_database

    db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
    db["demographics"] = preprocess_demographics_database(db["demographics"])
    db["interventions"] = preprocess_interventions_database(db["interventions"])
    db["cohorts"] = preprocess_cohorts_database(db["cohorts"])

    cohorts_rand = db["cohorts"].copy(deep=True)
    cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
    database_dict = {
        "demographics": db["demographics"],
        "diagnoses": db["diagnoses"],
        "pharma": db["pharma"],
        "interventions": db["interventions"],
        "physical_exams": db["physical_exams"],
        "cohorts": cohorts_rand
    }

    tab = mb2_tab0(
        dict_of_tables= database_dict  # db
    )
    app = tab.get_panel(language_code="it", disease_code="_depression_")
    app.show()


    tab = mb2_tab1()
    app = tab.get_panel(language_code="it")
    app.show()
    quit()