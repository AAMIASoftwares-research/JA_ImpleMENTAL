import os, sys, time

import warnings
# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)


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
from .loading import Loading
from .main_selectors import DiseaseSelector, IndicatorTypeSelector, CohortSelector
# database is loaded in the .database.database module, 
# and imported in the .indicator.dispatcher module.
from .indicator.dispatcher import dispatcher_instance


if __name__ == "__main__":

    language_selector_instance = LanguageSelector()
    header_instance = Header()
    disease_selector_instance = DiseaseSelector()
    indicator_type_selector_instance = IndicatorTypeSelector()
    cohort_selector_instance = CohortSelector()
    footer_instance = Footer()
    loading_animation_instance = Loading()
    from .loading.loading import widg_increase, widg_decrease # useful just here to put it in the dashboard app

    APP = panel.Column(
        language_selector_instance.get_panel(),
        panel.bind(header_instance.get_panel, language_selector_instance.widget),
        panel.bind(disease_selector_instance.get_panel, language_selector_instance.widget, disease_selector_instance.widget),
        panel.bind(indicator_type_selector_instance.get_panel, language_selector_instance.widget),
        panel.bind(cohort_selector_instance.get_panel, language_selector_instance.widget, indicator_type_selector_instance.widget, cohort_selector_instance.widget),
        panel.bind(dispatcher_instance.get_panel, 
                   language_selector_instance.widget, 
                   disease_selector_instance.widget, 
                   indicator_type_selector_instance.widget, 
                   cohort_selector_instance.widget
        ),
        panel.bind(footer_instance.get_panel, language_selector_instance.widget),
        panel.pane.HTML("</br style='padding-top: 200px;'>"),
        loading_animation_instance.get_panel(), widg_increase, widg_decrease
    )
    APP.show()