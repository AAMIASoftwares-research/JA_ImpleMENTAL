import os, sys, time

import panel
from ._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .language_selector import LanguageSelector
from .header import Header
from .footer import Footer
from .main_selectors import DiseaseSelector, IndicatorTypeSelector, CohortSelector

def make_html_prova(lang_code, disease_code, indicator_type_code, cohort_code):
        print(lang_code, disease_code, indicator_type_code, cohort_code)
        return panel.pane.HTML(
              f"""<h2></br></br></br></br></br>
              Lang code: {lang_code}</br>
              Disease code: {disease_code}</br>
              Indicator type code: {indicator_type_code}</br>
              </h2>""")
    

if __name__ == "__main__":

    language_selector_instance = LanguageSelector()
    header_instance = Header()
    disease_selector_instance = DiseaseSelector()
    indicator_type_selector_instance = IndicatorTypeSelector()
    cohort_selector_instance = CohortSelector()

    footer_instance = Footer()
    APP = panel.Column(
        language_selector_instance.get_panel(),
        panel.bind(header_instance.get_panel, language_selector_instance.widget),
        panel.bind(disease_selector_instance.get_panel, language_selector_instance.widget, disease_selector_instance.widget),
        panel.bind(indicator_type_selector_instance.get_panel, language_selector_instance.widget),
        panel.bind(cohort_selector_instance.get_panel, language_selector_instance.widget, indicator_type_selector_instance.widget, cohort_selector_instance.widget),
        panel.bind(make_html_prova, 
                   language_selector_instance.widget, 
                   disease_selector_instance.widget, 
                   indicator_type_selector_instance.widget, 
                   cohort_selector_instance.widget
        ),
        panel.bind(footer_instance.get_panel, language_selector_instance.widget)
    )
    APP.show()