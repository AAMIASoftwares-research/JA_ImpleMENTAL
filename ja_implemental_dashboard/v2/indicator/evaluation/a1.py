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
import bokeh.events
import bokeh.plotting

from ...database.database import DISEASE_CODE_TO_DB_CODE, COHORT_CODE_TO_DB_CODE
from ..logic_utilities import clean_indicator_getter_input, stratify_demographics
from ..widget import indicator_widget
from ...main_selectors.disease_text import DS_TITLE as DISEASES_LANGDICT
from ...main_selectors.cohort_text import COHORT_NAMES


# indicator logic
def ea1(**kwargs):
    """
    output dict:
    - percentage (float): the indicator, ranage [0; 1]; 
    - distribution (list): the distribution of number of intervention per patient
    if the patient has at least one intervention
    """
    # inputs
    kwargs = clean_indicator_getter_input(**kwargs)
    tables = kwargs.get("dict_of_tables", None)
    disease_db_code = kwargs.get("disease_db_code", None)
    cohort_db_code = COHORT_CODE_TO_DB_CODE[kwargs.get("cohort_code", None)]
    year_of_inclusion = kwargs.get("year_of_inclusion", None)
    age = kwargs.get("age", None)
    gender = kwargs.get("gender", None)
    civil_status = kwargs.get("civil_status", None)
    job_condition = kwargs.get("job_condition", None)
    educational_level = kwargs.get("educational_level", None)
    # output
    # type_int: any intervention
    # percentage (float): the indicator, ranage [0; 1]; 
    # distribution (list): the distribution of number of intervention per patient
    #  if the patient has at least one intervention
    statistics_keys = ["percentage", "distribution"]
    output = {k0: None for k0 in statistics_keys}
    # logic
    # - get a list of patient ids that are compatible with the stratification parameters
    valid_patient_ids = stratify_demographics(
        tables["demographics"],
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    # - stratify patients by disease: from valid_patient_ids, select only the ones that in the cohorts
    # table have at least one entry for the desired disease
    ids_with_disease: numpy.ndarray = tables["cohorts"].loc[
        (tables["cohorts"][disease_db_code] == "Y") & (tables["cohorts"]["YEAR_ENTRY"] <= year_of_inclusion),
        "ID_SUBJECT"
    ].unique()
    valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_with_disease)]
    # - stratify by patient cohort (_a_, _b_, _c_)
    ids_in_cohort: numpy.ndarray = tables["cohorts"].loc[tables["cohorts"][cohort_db_code] == "Y", "ID_SUBJECT"].unique()
    valid_patient_ids = valid_patient_ids[valid_patient_ids.isin(ids_in_cohort)]
    # - percentage denominator: number of patients with valid patient ids
    denominator = valid_patient_ids.unique().shape[0]
    # - percentage numerator: number of patients with at least one intervention in the year of inclusion
    condition = pandas.Series(True, index=tables["interventions"].index, name="condition")
    condition = condition & (tables["interventions"]["ID_SUBJECT"].isin(valid_patient_ids))
    condition = condition & (tables["interventions"]["DT_INT"].dt.year == year_of_inclusion)
    numerator = tables["interventions"].loc[condition, "ID_SUBJECT"].unique().shape[0]
    # - percentage
    output["percentage"] = numerator / denominator if denominator > 0 else 0.0
    # - distribution: we use the same condition as before but we count the number of interventions per ID_SUBJECT
    val_counts = tables["interventions"].loc[condition, "ID_SUBJECT"].value_counts()
    if len(val_counts) > 0:
        output["distribution"] = val_counts.to_list()
    else:
        output["distribution"] = [0, 0]
    # return
    return output


# Indicator display
ea1_code = "EA1"
ea1_name_langdict = {
    "en": "Access to community care",
    "it": "Accesso alle cure comunitarie",
    "fr": "Accès aux soins communautaires",
    "de": "Zugang zur Gemeindeversorgung",
    "es": "Acceso a la atención comunitaria",
    "pt": "Acesso aos cuidados comunitários"
}
ea1_short_desription_langdict = {
    "en": """Percentage of patients with at least one outpatient community contact.""",
    "it": """Percentuale di pazienti con almeno un contatto ambulatoriale con la comunità.""",
    "fr": """Pourcentage de patients ayant au moins un contact communautaire ambulatoire.""",
    "de": """Prozentsatz der Patienten mit mindestens einem ambulanten Gemeindekontakt.""",
    "es": """Porcentaje de pacientes con al menos un contacto comunitario ambulatorio.""",
    "pt": """Percentagem de pacientes com pelo menos um contacto comunitário ambulatório."""
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

ea1_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}

class ea1_tab0(object):
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
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        cohort_code = kwargs.get("cohort_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        ea1_list = []
        for year in years_to_evaluate:
            ea1_ = ea1(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                cohort_db_code=cohort_code,
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            ea1_list.append(100*ea1_["percentage"])
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
            title=ea1_code + " - " + ea1_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
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
            years_to_evaluate, ea1_list,
            line_color="#FF204Eff" # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
        )
        plot.circle(
            years_to_evaluate, ea1_list,
            fill_color="#FF204Eff", # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
            line_width=0,
            size=10
        )
        plot.add_tools(hover_tool)
        plot.toolbar.autohide = True
        plot.toolbar.logo = None
        out = panel.pane.Bokeh(plot)
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

ea1_tab_names_langdict["en"].append("Indicator distribution boxplot")
ea1_tab_names_langdict["it"].append("Distribuzione dell'indicatore con boxplot")
ea1_tab_names_langdict["fr"].append("Distribution de l'indicateur avec boxplot")
ea1_tab_names_langdict["de"].append("Indikatorverteilung Boxplot")
ea1_tab_names_langdict["es"].append("Distribución del indicador con boxplot")
ea1_tab_names_langdict["pt"].append("Distribuição do indicador com boxplot")

class ea1_tab1(object):
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
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        cohort_code = kwargs.get("cohort_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        ea1_dist_list = []
        for year in years_to_evaluate:
            ea1_ = ea1(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                cohort_db_code=cohort_code,
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            ea1_dist_list.append(
                ea1_["distribution"]
            )
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea1_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea1_dist_list[i])
        plot = holoviews.BoxWhisker(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False, 
            box_fill_color="#d3e3fd", 
            title=ea1_code + " - " + ea1_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea1_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea1_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea1_dist_list[i], 75) - numpy.percentile(ea1_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
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
    

ea1_tab_names_langdict["en"].append("Indicator distribution violin plot")
ea1_tab_names_langdict["it"].append("Distribuzione dell'indicatore con violino")
ea1_tab_names_langdict["fr"].append("Distribution de l'indicateur avec violon")
ea1_tab_names_langdict["de"].append("Indikatorverteilung Geigenplot")
ea1_tab_names_langdict["es"].append("Distribución del indicador con violín")
ea1_tab_names_langdict["pt"].append("Distribuição do indicador com violino")

class ea1_tab2(object):
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
        language_code = kwargs.get("language_code", "en")
        disease_code = kwargs.get("disease_code", None)
        cohort_code = kwargs.get("cohort_code", None)
        age = self.widgets_instance.widget_age_instance.value
        gender = kwargs.get("gender", None)
        civil_status = kwargs.get("civil_status", None)
        job_condition = kwargs.get("job_condition", None)
        educational_level = kwargs.get("educational_level", None)
        # logic
        years_to_evaluate = self._dict_of_tables["cohorts"]["YEAR_ENTRY"].unique().tolist()
        years_to_evaluate.sort()
        ea1_dist_list = []
        for year in years_to_evaluate:
            ea1_ = ea1(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                cohort_db_code=cohort_code,
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            ea1_dist_list.append(
                ea1_["distribution"]
            )
        # plot: BoxWhisker (not available in Bokeh)
        # make a BoxWhisker plot
        # groups (the years)
        # cathegory (the type of intervention, sub-years)
        # value (the distribution of the number of interventions)
        g_ = []
        v_ = []
        for i, y_ in enumerate(years_to_evaluate):
            n = len(ea1_dist_list[i])
            g_.extend([y_] * n)
            v_.extend(ea1_dist_list[i])
        plot = holoviews.Violin(
            (g_, v_), 
            kdims=[("year", _year_langdict[language_code])], 
            vdims=[("dist", _number_of_interventions_langdict[language_code])]
        ).opts(
            show_legend=False,
            inner="quartiles",
            bandwidth=0.5,
            violin_color="#d3e3fd", 
            title=ea1_code + " - " + ea1_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code] + ", " + COHORT_NAMES[language_code][cohort_code],
        )
        bokeh_plot = holoviews.render(plot)
        # add a transparent Circle plot to show some info with a custom hover tool
        source = bokeh.models.ColumnDataSource({
            "year": [str(i) for i in years_to_evaluate],
            "median": [numpy.median(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "mean": [numpy.mean(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "stdev": [numpy.std(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
            "q1": [numpy.percentile(ea1_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "q3": [numpy.percentile(ea1_dist_list[i], 75) for i in range(len(years_to_evaluate))],
            "iqr": [numpy.percentile(ea1_dist_list[i], 75) - numpy.percentile(ea1_dist_list[i], 25) for i in range(len(years_to_evaluate))],
            "count": [len(ea1_dist_list[i]) for i in range(len(years_to_evaluate))],
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

ea1_tab_names_langdict["en"].append("Help")
ea1_tab_names_langdict["it"].append("Aiuto")
ea1_tab_names_langdict["fr"].append("Aide")
ea1_tab_names_langdict["de"].append("Hilfe")
ea1_tab_names_langdict["es"].append("Ayuda")
ea1_tab_names_langdict["pt"].append("Ajuda")


class ea1_tab3(object):
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
                    The indicator is calculated as the percentage of patients having at least one outpatient community contact in the year of inclusion.
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
                    L'indicatore è calcolato come la percentuale di pazienti che hanno almeno un contatto ambulatoriale con la comunità nell'anno di inclusione.
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
                    L'indicateur est calculé comme le pourcentage de patients ayant au moins un contact communautaire ambulatoire dans l'année d'inclusion.
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
                    Der Indikator wird als Prozentsatz der Patienten berechnet, die mindestens einen ambulanten Gemeindekontakt im Jahr der Aufnahme haben.
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
                    El indicador se calcula como el porcentaje de pacientes que tienen al menos un contacto ambulatorio con la comunidad en el año de inclusión.
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
                    O indicador é calculado como a percentagem de pacientes que têm pelo menos um contacto ambulatório com a comunidade no ano de inclusão.
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

    quit()