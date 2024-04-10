import numpy
import pandas
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
from ..logic_utilities import clean_indicator_getter_input, stratify_demographics
from ..widget import indicator_widgets
from ...main_selectors.disease_text import DS_TITLE as DISEASES_LANGDICT

# indicator logic
def ma1(**kwargs):
    """
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
    ma1 = {
        "all": None,     # patients with any disease
        "selected": None # patients with the selected disease
    }
    # logic
    # - first find stratified demographics
    stratified_demographics_patient_ids = stratify_demographics(
        tables["demographics"],
        year_of_inclusion=year_of_inclusion,
        age=age,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level
    )
    # - from the cohort table, find the PREVALENT cohort with YEAR_ENTRY equal to year_of_inclusion
    condition = pandas.Series(numpy.repeat(True, tables["cohorts"].shape[0]))
    condition = condition & (tables["cohorts"]["ID_SUBJECT"].isin(stratified_demographics_patient_ids))
    condition = condition & (tables["cohorts"]["PREVALENT"] == "Y")
    condition = condition & (tables["cohorts"]["YEAR_ENTRY"] == year_of_inclusion)
    # - get indicator for all diseases
    ma1["all"] = tables["cohorts"].loc[condition, "ID_SUBJECT"].nunique()
    # - get indicator for selected disease
    condition = condition & (tables["cohorts"][disease_db_code] == "Y")
    ma1["selected"] = tables["cohorts"].loc[condition, "ID_SUBJECT"].nunique()
    # return
    return ma1


# Indicator display
ma1_code = "MA1"
ma1_name_langdict = {
    "en": "Treated prevalence",
    "it": "Prevalenza trattata",
    "fr": "Prévalence traitée",
    "de": "Behandlungsprävalenz",
    "es": "Prevalencia tratada",
    "pt": "Prevalência tratada"
}
ma1_short_desription_langdict = {
    "en": """Number of patients with a prevalent mental disorder
            treated in inpatient and outpatient Mental Health Facilities
            (for each year of data availability).""",
    "it": """Numero di pazienti con un disturbo mentale prevalente
            trattati in strutture di salute mentale ospedaliere e ambulatoriali
            (per ciascun anno di disponibilità dei dati).""",
    "fr": """Nombre de patients avec un trouble mental prévalent
            traités dans des établissements de santé mentale hospitaliers et ambulatoires
            (pour chaque année de disponibilité des données).""",
    "de": """Anzahl der Patienten mit einer vorherrschenden psychischen Störung,
            die in stationären und ambulanten Einrichtungen für psychische Gesundheit behandelt werden
            (für jedes Jahr der Datenverfügbarkeit).""",
    "es": """Número de pacientes con un trastorno mental prevalente
            tratados en instalaciones de salud mental hospitalarias y ambulatorias
            (para cada año de disponibilidad de datos).""",
    "pt": """Número de pacientes com um transtorno mental prevalente
            tratados em instalações de saúde mental hospitalares e ambulatoriais
            (para cada ano de disponibilidade de dados)."""
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

ma1_tab_names_langdict: dict[str: list[str]] = {
    "en": ["Indicator"],
    "it": ["Indicatore"],
    "fr": ["Indicateur"],
    "de": ["Indikator"],
    "es": ["Indicador"],
    "pt": ["Indicador"]
}

class ma1_tab0(object):
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
        ma1_all = []
        ma1_selected = []
        for year in years_to_evaluate:
            ma1_ = ma1(
                dict_of_tables=self._dict_of_tables,
                disease_db_code=DISEASE_CODE_TO_DB_CODE[disease_code],
                year_of_inclusion=year,
                age=age,
                gender=gender,
                civil_status=civil_status,
                job_condition=job_condition,
                educational_level=educational_level
            )
            ma1_all.append(ma1_["all"])
            ma1_selected.append(ma1_["selected"])
        # plot - use bokeh because it allows independent zooming
        _y_max_plot = max(max(ma1_all), max(ma1_selected))
        _y_max_plot *= 1.15
        hover_tool = bokeh.models.HoverTool(
            tooltips=[
                (_year_langdict[language_code], "@x"),
                (_number_of_patients_langdict[language_code], "@y")
            ]
        )
        plot = bokeh.plotting.figure(
            sizing_mode="stretch_width",
            height=350,
            title=ma1_code + " - " + ma1_name_langdict[language_code] + " - " + DISEASES_LANGDICT[language_code][disease_code],
            x_axis_label=_year_langdict[language_code],
            x_range=(years_to_evaluate[0]-0.5, years_to_evaluate[-1]+0.5),
            y_axis_label=_number_of_patients_langdict[language_code],
            y_range=(0, _y_max_plot),
            tools="pan,wheel_zoom,box_zoom,reset,save",
            toolbar_location="right",
        )
        plot.xaxis.ticker = numpy.sort(years_to_evaluate)
        plot.xgrid.grid_line_color = None
        plot.line(
            years_to_evaluate, ma1_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            line_color="#a0a0a0ff"
        )
        plot.circle(
            x=years_to_evaluate, 
            y=ma1_all,
            legend_label=DISEASES_LANGDICT[language_code]["_all_"],
            fill_color="#a0a0a0ff",
            line_width=0,
            size=10
        )
        plot.line(
            years_to_evaluate, ma1_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            line_color="#FF204Eff" # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
        )
        plot.circle(
            years_to_evaluate, ma1_selected,
            legend_label=DISEASES_LANGDICT[language_code][disease_code],
            fill_color="#FF204Eff", # https://colorhunt.co/palette/ff204ea0153e5d0e4100224d
            line_width=0,
            size=10
        )
        plot.add_tools(hover_tool)
        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        plot.toolbar.autohide = True
        plot.toolbar.logo = None
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
        

ma1_tab_names_langdict["en"].append("Help")
ma1_tab_names_langdict["it"].append("Aiuto")
ma1_tab_names_langdict["fr"].append("Aide")
ma1_tab_names_langdict["de"].append("Hilfe")
ma1_tab_names_langdict["es"].append("Ayuda")
ma1_tab_names_langdict["pt"].append("Ajuda")


class ma1_tab1(object):
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
                    The treated prevalence indicator calculates the number of patients 
                    with a prevalent mental disorder who are treated in inpatient and 
                    outpatient Mental Health Facilities. It takes into account various 
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
                    L'indicatore di prevalenza trattata calcola il numero di pazienti 
                    con un disturbo mentale prevalente trattati in strutture di salute mentale 
                    ospedaliere e ambulatoriali. Considera vari fattori demografici come 
                    anno di inclusione, età, genere, stato civile, condizione lavorativa e 
                    livello di istruzione.
                    </p>

                    <h3 style='{h3_style}'>Visualizzazione dell'indicatore</h3>
                    <p style='{p_style}'>
                    L'indicatore è visualizzato come un grafico che mostra il numero di pazienti 
                    nel corso degli anni di disponibilità dei dati. L'asse x rappresenta gli anni, 
                    mentre l'asse y rappresenta il numero di pazienti. 
                    Il grafico è stratificato per malattia, consentendo di selezionare una malattia 
                    specifica per visualizzarne la prevalenza trattata nel tempo.
                    </p>
                """,
            "fr":
                f"""
                    <h3 style='{h3_style}'>Calcul de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur de prévalence traitée calcule le nombre de patients 
                    atteints d'un trouble mental prévalent traités dans des établissements 
                    de santé mentale hospitaliers et ambulatoires. Il prend en compte divers 
                    facteurs démographiques tels que l'année d'inclusion, l'âge, le genre, 
                    l'état civil, la condition de travail et le niveau d'éducation.
                    </p>

                    <h3 style='{h3_style}'>Affichage de l'indicateur</h3>
                    <p style='{p_style}'>
                    L'indicateur est affiché sous forme de graphique montrant le nombre de patients 
                    au fil des années de disponibilité des données. L'axe des x représente les années, 
                    et l'axe des y représente le nombre de patients. 
                    Le graphique est stratifié par maladie, vous permettant de sélectionner une maladie 
                    spécifique pour visualiser sa prévalence traitée au fil du temps.
                    </p>
                """,
            "de":
                f"""
                    <h3 style='{h3_style}'>Indikatorberechnung</h3>
                    <p style='{p_style}'>
                    Der Indikator für die behandelte Prävalenz berechnet die Anzahl von Patienten 
                    mit einer vorherrschenden psychischen Störung, die in stationären und ambulanten 
                    Einrichtungen für psychische Gesundheit behandelt werden. Er berücksichtigt verschiedene 
                    demografische Faktoren wie das Jahr der Aufnahme, das Alter, das Geschlecht, den Familienstand, 
                    die Berufsbedingungen und das Bildungsniveau.
                    </p>

                    <h3 style='{h3_style}'>Indikatoranzeige</h3>
                    <p style='{p_style}'>
                    Der Indikator wird als Diagramm dargestellt, das die Anzahl der Patienten 
                    über die Jahre der Datenverfügbarkeit zeigt. Die x-Achse repräsentiert die Jahre, 
                    und die y-Achse repräsentiert die Anzahl der Patienten. 
                    Das Diagramm ist nach Krankheit stratifiziert, sodass Sie eine bestimmte Krankheit 
                    auswählen können, um ihre behandelte Prävalenz im Laufe der Zeit anzuzeigen.
                    </p>
                """,
            "es":
                f"""
                    <h3 style='{h3_style}'>Cálculo del indicador</h3>
                    <p style='{p_style}'>
                    El indicador de prevalencia tratada calcula el número de pacientes 
                    con un trastorno mental prevalente tratados en instalaciones de salud mental 
                    hospitalarias y ambulatorias. Toma en cuenta varios factores demográficos 
                    como el año de inclusión, la edad, el género, el estado civil, la condición laboral 
                    y el nivel educativo.
                    </p>

                    <h3 style='{h3_style}'>Visualización del indicador</h3>
                    <p style='{p_style}'>
                    El indicador se muestra como un gráfico que muestra el número de pacientes 
                    a lo largo de los años de disponibilidad de datos. El eje x representa los años, 
                    y el eje y representa el número de pacientes. 
                    El gráfico está estratificado por enfermedad, lo que le permite seleccionar una enfermedad 
                    específica para ver su prevalencia tratada a lo largo del tiempo.
                    </p>
                """,
            "pt":
                f"""
                    <h3 style='{h3_style}'>Cálculo do indicador</h3>
                    <p style='{p_style}'>
                    O indicador de prevalência tratada calcula o número de pacientes 
                    com um transtorno mental prevalente tratados em instalações de saúde mental 
                    hospitalares e ambulatoriais. Leva em consideração vários fatores demográficos 
                    como ano de inclusão, idade, gênero, estado civil, condição de trabalho e 
                    nível educacional.
                    </p>

                    <h3 style='{h3_style}'>Exibição do indicador</h3>
                    <p style='{p_style}'>
                    O indicador é exibido como um gráfico que mostra o número de pacientes 
                    ao longo dos anos de disponibilidade de dados. O eixo x representa os anos, 
                    e o eixo y representa o número de pacientes. 
                    O gráfico é estratificado por doença, permitindo que você selecione uma doença 
                    específica para ver sua prevalência tratada ao longo do tempo.
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

    tab = ma1_tab0(
        dict_of_tables= database_dict  # db
    )
    app = tab.get_panel(language_code="it", disease_code="_depression_")
    app.show()


    tab = ma1_tab1()
    app = tab.get_panel(language_code="it")
    app.show()
    quit()