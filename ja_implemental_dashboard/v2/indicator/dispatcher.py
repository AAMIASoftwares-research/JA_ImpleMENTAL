import time
import sqlite3
import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)
# This is the class to dispatch the monitoring and evaluation columns
# This will be included into the final dashboard column
# All indicators and their logic will be included here

from .indicator_panel import IndicatorPanel, EmptyPanel
from ..loading.loading import increase_loading_counter, decrease_loading_counter


class Dispatcher(object):
    def __init__(self, monitoring_panel_classes: list[IndicatorPanel], evaluation_panel_classes: list[IndicatorPanel]):
        self._monitoring_panel_classes = monitoring_panel_classes
        self._evaluation_panel_classes = evaluation_panel_classes
        # pane styles
        self._pane_styles = {
            "display": "flex",
            "flex-direction": "column",
            "justify-content": "center",
            "align-items": "center",
        }
        self._pane_stylesheet = ""
        self._pane = None

    def get_panel(self, language_code, disease_code, indicator_type_code, cohort_code):
        increase_loading_counter()
        # ALL DISEASES
        if disease_code == "_all_":
            pane = panel.Column(
                panel.pane.HTML("<h3 style='text-align: center;'>Choose a disorder from the dropdown menu to start.</h3><p style='text-align: center;'>Beware! Computing indicators may take a while<br/>the first time the Dashboard starts.</p>"),
                styles={
                    "margin": "auto",
                    "height": "250px",
                    # align content horizontaly in the center
                    "display": "flex",
                    "flex-direction": "row",
                    "justify-content": "center",
                    "align-items": "center",
                },
                stylesheets=[self._pane_stylesheet]
            )
            return pane
        # SELECTED DISEASE
        if indicator_type_code == "_monitoring_":
            panes_list = [
                p.get_panel(language_code=language_code, disease_code=disease_code) 
                for p in self._monitoring_panel_classes 
            ]
        elif indicator_type_code == "_evaluation_":
            panes_list = [
                p.get_panel(language_code=language_code, disease_code=disease_code, cohort_code=cohort_code)
                for p in self._evaluation_panel_classes
            ]
        else:
            raise ValueError("Indicator type not recognized:", indicator_type_code)
        if self._pane is not None:
            # update
            self._pane[:] = panes_list
            return self._pane
        else:
            self._pane = panel.Column(
                *panes_list,
                styles=self._pane_styles,
                stylesheets=[self._pane_stylesheet]
            )
        decrease_loading_counter()
        return self._pane


# Make all indicator panels to be displayed in the dashboard
# This line will trigger the loading of the database from the user
# and the preprocessing of it.
# Check out load_database for the whole process
from ..database.load_database import DB
from .indicator_panel import SectionDividerPanel

# Monitoring indicators

ma_section_divider = SectionDividerPanel(
    section_title_langdict={
        "en": "A. TREATED PREVALENCE AND INCIDENCE IN MENTAL HEALTH SERVICES",
        "it": "A. PREVALENZA E INCIDENZA TRATTATA NEI SERVIZI DI SALUTE MENTALE",
        "fr": "A. PRÉVALENCE ET INCIDENCE TRAITÉES DANS LES SERVICES DE SANTÉ MENTALE",
        "de": "A. BEHANDELTE PRÄVALENZ UND INZIDENZ IN PSYCHIATRISCHEN DIENSTEN",
        "es": "A. PREVALENCIA E INCIDENCIA TRATADAS EN LOS SERVICIOS DE SALUD MENTAL",
        "pt": "A. PREVALÊNCIA E INCIDÊNCIA TRATADAS NOS SERVIÇOS DE SAÚDE MENTAL",
    },
    is_first_in_page=True
)

from .monitoring.a1 import (
    ma1_code, ma1_name_langdict, ma1_short_desription_langdict,
    ma1_tab_names_langdict,
    ma1_tab0, ma1_tab1
)
ma1_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=ma1_code,
    indicator_name=ma1_name_langdict,
    indicator_short_description=ma1_short_desription_langdict,
    tabs=[ma1_tab0(DB), ma1_tab1()],
    tab_names_langdict=ma1_tab_names_langdict
)
from .monitoring.a2 import (
    ma2_code, ma2_name_langdict, ma2_short_desription_langdict,
    ma2_tab_names_langdict,
    ma2_tab0, ma2_tab1
)
ma2_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=ma2_code,
    indicator_name=ma2_name_langdict,
    indicator_short_description=ma2_short_desription_langdict,
    tabs=[ma2_tab0(DB), ma2_tab1()],
    tab_names_langdict=ma2_tab_names_langdict
)
from .monitoring.a3 import (
    ma3_code, ma3_name_langdict, ma3_short_desription_langdict,
    ma3_tab_names_langdict,
    ma3_tab0, ma3_tab1
)
ma3_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=ma3_code,
    indicator_name=ma3_name_langdict,
    indicator_short_description=ma3_short_desription_langdict,
    tabs=[ma3_tab0(DB), ma3_tab1()],
    tab_names_langdict=ma3_tab_names_langdict
)
mb_section_divider = SectionDividerPanel(
    section_title_langdict={
        "en": "B. OUTPATIENT CARE",
        "it": "B. CURA AMBULATORIALE",
        "fr": "B. SOINS AMBULATOIRES",
        "de": "B. AMBULANTE VERSORGUNG",
        "es": "B. ATENCIÓN AMBULATORIA",
        "pt": "B. CUIDADOS AMBULATORIAIS",
    }
)

from .monitoring.b2 import (
    mb2_code, mb2_name_langdict, mb2_short_desription_langdict,
    mb2_tab_names_langdict,
    mb2_tab0, mb2_tab1, mb2_tab2, mb2_tab3
)
mb2_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=mb2_code,
    indicator_name=mb2_name_langdict,
    indicator_short_description=mb2_short_desription_langdict,
    tabs=[mb2_tab0(DB), mb2_tab1(DB), mb2_tab2(DB), mb2_tab3()],
    tab_names_langdict=mb2_tab_names_langdict
)
# Evaluation indicators
ea_section_divider = SectionDividerPanel(
    section_title_langdict={
        "en": "A. ACCESSIBILITY",
        "it": "A. ACCESSIBILITÀ",
        "fr": "A. ACCESSIBILITÉ",
        "de": "A. ZUGÄNGLICHKEIT",
        "es": "A. ACCESIBILIDAD",
        "pt": "A. ACESSIBILIDADE",
    },
    is_first_in_page=True
)
from .evaluation.a1 import (
    ea1_code, ea1_name_langdict, ea1_short_desription_langdict,
    ea1_tab_names_langdict,
    ea1_tab0, ea1_tab1, ea1_tab2, ea1_tab3
)
ea1_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea1_code,
    indicator_name=ea1_name_langdict,
    indicator_short_description=ea1_short_desription_langdict,
    tabs=[ea1_tab0(DB), ea1_tab1(DB), ea1_tab2(DB), ea1_tab3()],
    tab_names_langdict=ea1_tab_names_langdict
)
from .evaluation.a2 import (
    ea2_code, ea2_name_langdict, ea2_short_desription_langdict,
    ea2_tab_names_langdict,
    ea2_tab0, ea2_tab1, ea2_tab2, ea2_tab3
)
ea2_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea2_code,
    indicator_name=ea2_name_langdict,
    indicator_short_description=ea2_short_desription_langdict,
    tabs=[ea2_tab0(DB), ea2_tab1(DB), ea2_tab2(DB), ea2_tab3()],
    tab_names_langdict=ea2_tab_names_langdict
)
from .evaluation.a3 import (
    ea3_code, ea3_name_langdict, ea3_short_desription_langdict,
    ea3_tab_names_langdict,
    ea3_tab0, ea3_tab1, ea3_tab2, ea3_tab3
)
ea3_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea3_code,
    indicator_name=ea3_name_langdict,
    indicator_short_description=ea3_short_desription_langdict,
    tabs=[ea3_tab0(DB), ea3_tab1(DB), ea3_tab2(DB), ea3_tab3()],
    tab_names_langdict=ea3_tab_names_langdict
)
from .evaluation.a4 import (
    ea4_code, ea4_name_langdict, ea4_short_desription_langdict,
    ea4_tab_names_langdict,
    ea4_tab0, ea4_tab1, ea4_tab2, ea4_tab3
)
ea4_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea4_code,
    indicator_name=ea4_name_langdict,
    indicator_short_description=ea4_short_desription_langdict,
    tabs=[ea4_tab0(DB), ea4_tab1(DB), ea4_tab2(DB), ea4_tab3()],
    tab_names_langdict=ea4_tab_names_langdict
)
from .evaluation.a5 import (
    ea5_code, ea5_name_langdict, ea5_short_desription_langdict,
    ea5_tab_names_langdict,
    ea5_tab0, ea5_tab1, ea5_tab2, ea5_tab3
)
ea5_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea5_code,
    indicator_name=ea5_name_langdict,
    indicator_short_description=ea5_short_desription_langdict,
    tabs=[ea5_tab0(DB), ea5_tab1(DB), ea5_tab2(DB), ea5_tab3()],
    tab_names_langdict=ea5_tab_names_langdict
)
from .evaluation.a60 import (
    ea60_code, ea60_name_langdict, ea60_short_desription_langdict,
    ea60_tab_names_langdict,
    ea60_tab0, ea60_tab1, ea60_tab2, ea60_tab3
)
ea60_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea60_code,
    indicator_name=ea60_name_langdict,
    indicator_short_description=ea60_short_desription_langdict,
    tabs=[ea60_tab0(DB), ea60_tab1(DB), ea60_tab2(DB), ea60_tab3()],
    tab_names_langdict=ea60_tab_names_langdict
)
from .evaluation.a61 import (
    ea61_code, ea61_name_langdict, ea61_short_desription_langdict,
    ea61_tab_names_langdict,
    ea61_tab0, ea61_tab1, ea61_tab2, ea61_tab3
)
ea61_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea61_code,
    indicator_name=ea61_name_langdict,
    indicator_short_description=ea61_short_desription_langdict,
    tabs=[ea61_tab0(DB), ea61_tab1(DB), ea61_tab2(DB), ea61_tab3()],
    tab_names_langdict=ea61_tab_names_langdict
)
from .evaluation.a62 import (
    ea62_code, ea62_name_langdict, ea62_short_desription_langdict,
    ea62_tab_names_langdict,
    ea62_tab0, ea62_tab1, ea62_tab2, ea62_tab3
)
ea62_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code=ea62_code,
    indicator_name=ea62_name_langdict,
    indicator_short_description=ea62_short_desription_langdict,
    tabs=[ea62_tab0(DB), ea62_tab1(DB), ea62_tab2(DB), ea62_tab3()],
    tab_names_langdict=ea62_tab_names_langdict
)


from .indicator_panel import PlaceholderPanel

monitor_panel_classes_list = [
    ma_section_divider,
    ma1_indicator_panel,
    ma2_indicator_panel,
    ma3_indicator_panel,
    mb_section_divider,
    mb2_indicator_panel,
]

evaluation_panel_classes_list = [
    ea_section_divider,
    ea1_indicator_panel,
    ea2_indicator_panel,
    ea3_indicator_panel,
    ea4_indicator_panel,
    ea5_indicator_panel,
    ea60_indicator_panel,
    ea61_indicator_panel,
    ea62_indicator_panel,
]





# Leave the rest to the dispatcher, nothing else to do here!

if len(monitor_panel_classes_list) == len(evaluation_panel_classes_list):
    evaluation_panel_classes_list.append(EmptyPanel(indicator_type="_evaluation_"))

dispatcher_instance = Dispatcher(
    monitoring_panel_classes=monitor_panel_classes_list,
    evaluation_panel_classes=evaluation_panel_classes_list
)









if __name__ == "__main__":
    # make some holoviz plots
    import numpy as np
    import pandas as pd
    import holoviews as hv
    hv.extension('bokeh')

    # PIE PLOT
    from math import pi
    from bokeh.palettes import Category20c, Category20
    from bokeh.plotting import figure
    from bokeh.transform import cumsum
    x = {
        'United States': 157,
        'United Kingdom': 93,
        'Japan': 89,
        'China': 63,
        'Germany': 44,
        'India': 42,
        'Italy': 40,
        'Australia': 35,
        'Brazil': 32,
        'France': 31,
        'Taiwan': 31,
        'Spain': 29
    }
    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = Category20c[len(x)]
    p = figure(height=350, title="Pie Chart", toolbar_location=None,
            tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))
    r = p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    bokeh_pane = panel.pane.Bokeh(p, theme="dark_minimal")

    # LINE PLOT
    xs = np.linspace(0, np.pi)
    curve = hv.Curve((xs, np.sin(xs)))
    holoviews_pane = panel.pane.HoloViews(curve)

    # An image from a random numpy array
    img = np.random.rand(256, 256)
    img_pane = panel.pane.HoloViews(hv.Image(img))

    # A simple html text
    html_pane = panel.pane.HTML("<h1>HTML here</h1><p>Some text, for example <span style='font-weight: 400; color=#ff7a34ff'>lorem ipsum.</span></p>")

    # make classes
    class dummy_viz_class:
        def __init__(self, pane: panel.viewable.Viewable):
            self._pane = pane

        def get_panel(self, **kwargs):
            return self._pane

    panes_classes = [dummy_viz_class(bokeh_pane), dummy_viz_class(holoviews_pane), dummy_viz_class(img_pane), dummy_viz_class(html_pane)]
    panes_names = ["Bokeh Pie Chart", "Holoviews Line Plot", "Random Image", "HTML Text"]

    # create the indicator panel
    indicator_panel_1 = IndicatorPanel(
        monitoring_or_evaluation="_monitoring_",
        indicator_code="MA1",
        indicator_name={"en": "Indicator name - <span style='font-weight: 400;'>with styling</span>", "it": "Nome indicatore"},
        indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
        tabs=panes_classes,
        tab_names_langdict={"en": panes_names, "it": panes_names}
    )

    indicator_panel_2 = IndicatorPanel(
        monitoring_or_evaluation="_monitoring_",
        indicator_code="MA2",
        indicator_name={"en": "Another indicator - <span style='font-weight: bold;'>without styling</span>", "it": "Nome indicatore"},
        indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
        tabs=panes_classes,
        tab_names_langdict={"en": panes_names, "it": panes_names}
    )


    # create the dashboard
    app = panel.Column(
        indicator_panel_1.get_panel(language_code="en", disease_code="_depression_"),
        indicator_panel_2.get_panel(language_code="en", disease_code="_depression_")
    )
    app.show()



    



        


