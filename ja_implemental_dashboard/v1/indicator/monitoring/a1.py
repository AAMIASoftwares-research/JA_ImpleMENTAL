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
        print(kwargs.get("civil_status"))
        plot = panel.pane.HTML(
            f"""<h2>
            ma1_tab0</br>
            </h2>
            <p>{kwargs}, age: {self.widgets_instance.widget_age_instance.value}</p>
            """
        )
        return plot

    def get_panel(self, language_code, disease_code):
        pane = panel.Row(
            panel.bind(
                self.get_plot, 
                language_code=language_code, 
                disease_code=disease_code,
                dict_of_tables=self._dict_of_tables,
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
    tab = ma1_tab0(
         language_code="en",
            dict_of_tables={}
    )
    app = tab.get_panel(language_code="en", disease_code="COPD")
    app.show()