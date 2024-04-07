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
holoviews.extension('bokeh')

from ..database import DISEASE_CODE_TO_DB_CODE
from ..logic_utilities import clean_indicator_getter_input, stratify_demographics
from ..widget import indicator_widgets

# text and constants in all languages

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




class ma1_tab0(object):
    def __init__(self, language_code: str, dict_of_tables: dict):
        self._language_code = language_code
        self._dict_of_tables = dict_of_tables
        self.widgets_instance = indicator_widgets(
             language_code=language_code,
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
        # plot
        plot_all = holoviews.Curve(
            (years_to_evaluate, ma1_all),
            label="All diseases",
        ).opts(
            title="Prevalent cohort",
            xlabel="Year",
            ylabel="Number of patients",
            color="blue"
        )
        out = panel.pane.HoloViews(
            plot_all
        )
        return out
    

    def get_panel(self, language_code, disease_code):
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
        
        


if __name__ == "__main__":
    from ..database import FILES_FOLDER, DATABASE_FILENAMES_DICT, read_databases, preprocess_demographics_database, preprocess_interventions_database, preprocess_cohorts_database

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
         language_code="en",
            dict_of_tables= database_dict  # db
    )
    app = tab.get_panel(language_code="en", disease_code="_depression_")
    app.show()