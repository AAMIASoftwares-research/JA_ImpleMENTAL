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
        # ALL DISEASES
        if disease_code == "_all_":
            pane = panel.Column(
                panel.pane.HTML("<h3>Choose a disorder</h3>"),
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
        return self._pane








# Load/Connect database here
#############################
# the database is loaded, DB is the sqlite3 connection object
# to the database.
from ..database.database import DB

# Standardize tables names
from ..database.database import standardize_table_names
standardize_table_names(DB)

# Check if the database has the necessary tables
from ..database.database import check_database_has_tables
is_ok, missing = check_database_has_tables(DB)
if not is_ok:
    raise ValueError("The database is missing the following tables which are required:", missing)

# Preprocess the database: fix data types
from ..database.database import preprocess_database_data_types, slim_down_database
preprocess_database_data_types(DB)

# Preprocess the database: create a second database file containing only patients
#                          that are mental health patients of some sort, to exclude
#                          every other medical condition
#
#          .................. TO DO .......................
#          forse non serve perche dovrebbero essere gia scremati,
#          ma per evitare errori, meglio fare un controllo
#          la scrematura maggiore puo avvenire a livello della tabella pharma
#          e demographics, perche le altre sono abbastanza specifiche
# new_db_path = slim_down_database(DB)
# DB.close()
# DB = sqlite3.connect(new_db_path)
print("Slimmed database file path:", slim_down_database(DB))


print("Database is ready!")
quit()


#
# Create the Cohorts table
from ..database.database import add_cohorts_table
# .......  TO DO ...........
# add_cohorts_temporary_table(DB)


# Create the stratified demographics table
from ..indicator.widget import AGE_WIDGET_INTERVALS
from ..database.database import make_age_startification_tables
years_of_inclusion = [2018, 2019, 2020, 2021] ########################### to do after having cohorts, and use function get_years_of_inclusion
make_age_startification_tables(DB, years_of_inclusion, AGE_WIDGET_INTERVALS)








# Make all indicator panels to be displayed in the dashboard

# Monitoring indicators

from .monitoring.a1 import (
    ma1_code, ma1_name_langdict, ma1_short_desription_langdict,
    ma1_tab_names_langdict,
    ma1_tab0, ma1_tab1
)
ma1_tab0_instance = ma1_tab0(DB)
ma1_tab1_instance = ma1_tab1()
ma1_indicator_panel = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=ma1_code,
    indicator_name=ma1_name_langdict,
    indicator_short_description=ma1_short_desription_langdict,
    tabs=[ma1_tab0_instance, ma1_tab1_instance],
    tab_names_langdict=ma1_tab_names_langdict
)

if 0:

    from .monitoring.a2 import (
        ma2_code, ma2_name_langdict, ma2_short_desription_langdict,
        ma2_tab_names_langdict,
        ma2_tab0, ma2_tab1
    )
    ma2_tab0_instance = ma2_tab0(__DB__)
    ma2_tab1_instance = ma2_tab1()
    ma2_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_monitoring_",
        indicator_code=ma2_code,
        indicator_name=ma2_name_langdict,
        indicator_short_description=ma2_short_desription_langdict,
        tabs=[ma2_tab0_instance, ma2_tab1_instance],
        tab_names_langdict=ma2_tab_names_langdict
    )

    from .monitoring.a3 import (
        ma3_code, ma3_name_langdict, ma3_short_desription_langdict,
        ma3_tab_names_langdict,
        ma3_tab0, ma3_tab1
    )
    ma3_tab0_instance = ma3_tab0(__DB__)
    ma3_tab1_instance = ma3_tab1()
    ma3_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_monitoring_",
        indicator_code=ma3_code,
        indicator_name=ma3_name_langdict,
        indicator_short_description=ma3_short_desription_langdict,
        tabs=[ma3_tab0_instance, ma3_tab1_instance],
        tab_names_langdict=ma3_tab_names_langdict
    )

    from .monitoring.b2 import (
        mb2_code, mb2_name_langdict, mb2_short_desription_langdict,
        mb2_tab_names_langdict,
        mb2_tab0, mb2_tab1, mb2_tab2, mb2_tab3
    )
    mb2_tab0_instance = mb2_tab0(__DB__)
    mb2_tab1_instance = mb2_tab1(__DB__)
    mb2_tab2_instance = mb2_tab2(__DB__)
    mb2_tab3_instance = mb2_tab3()

    mb2_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_monitoring_",
        indicator_code=mb2_code,
        indicator_name=mb2_name_langdict,
        indicator_short_description=mb2_short_desription_langdict,
        tabs=[mb2_tab0_instance, mb2_tab1_instance, mb2_tab2_instance, mb2_tab3_instance],
        tab_names_langdict=mb2_tab_names_langdict
    )

    # Evaluation indicators

    from .evaluation.a1 import (
        ea1_code, ea1_name_langdict, ea1_short_desription_langdict,
        ea1_tab_names_langdict,
        ea1_tab0, ea1_tab1, ea1_tab2, ea1_tab3
    )
    ea1_tab0_instance = ea1_tab0(__DB__)
    ea1_tab1_instance = ea1_tab1(__DB__)
    ea1_tab2_instance = ea1_tab2(__DB__)
    ea1_tab3_instance = ea1_tab3()

    ea1_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_evaluation_",
        indicator_code=ea1_code,
        indicator_name=ea1_name_langdict,
        indicator_short_description=ea1_short_desription_langdict,
        tabs=[ea1_tab0_instance, ea1_tab1_instance, ea1_tab2_instance, ea1_tab3_instance],
        tab_names_langdict=ea1_tab_names_langdict
    )

    from .evaluation.a2 import (
        ea2_code, ea2_name_langdict, ea2_short_desription_langdict,
        ea2_tab_names_langdict,
        ea2_tab0, ea2_tab1, ea2_tab2, ea2_tab3
    )
    ea2_tab0_instance = ea2_tab0(__DB__)
    ea2_tab1_instance = ea2_tab1(__DB__)
    ea2_tab2_instance = ea2_tab2(__DB__)
    ea2_tab3_instance = ea2_tab3()
    ea2_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_evaluation_",
        indicator_code=ea2_code,
        indicator_name=ea2_name_langdict,
        indicator_short_description=ea2_short_desription_langdict,
        tabs=[ea2_tab0_instance, ea2_tab1_instance, ea2_tab2_instance, ea2_tab3_instance],
        tab_names_langdict=ea2_tab_names_langdict
    )

    from .evaluation.a3 import (
        ea3_code, ea3_name_langdict, ea3_short_desription_langdict,
        ea3_tab_names_langdict,
        ea3_tab0, ea3_tab1, ea3_tab2, ea3_tab3
    )
    ea3_tab0_instance = ea3_tab0(__DB__)
    ea3_tab1_instance = ea3_tab1(__DB__)
    ea3_tab2_instance = ea3_tab2(__DB__)
    ea3_tab3_instance = ea3_tab3()
    ea3_indicator_panel = IndicatorPanel(
        monitoring_or_evaluation="_evaluation_",
        indicator_code=ea3_code,
        indicator_name=ea3_name_langdict,
        indicator_short_description=ea3_short_desription_langdict,
        tabs=[ea3_tab0_instance, ea3_tab1_instance, ea3_tab2_instance, ea3_tab3_instance],
        tab_names_langdict=ea3_tab_names_langdict
    )

# fake evaluation
from .indicator_panel import PlaceholderPanel

eb1_indicator_panel_placeholder = PlaceholderPanel(
    placeholder_html_string="<h2>EB1 panel goes here</h2>"
)

eb2_indicator_panel_placeholder = PlaceholderPanel(
    placeholder_html_string="<h2>EB2 panel goes here</h2>"
)
eb3_indicator_panel_placeholder = PlaceholderPanel(
    placeholder_html_string="<h2>EB3 panel goes here</h2>"
)

monitor_panel_classes_list = [
    ma1_indicator_panel, 
    # ma2_indicator_panel, 
    # ma3_indicator_panel,
    # mb2_indicator_panel
]

evaluation_panel_classes_list = [
    # ea1_indicator_panel,
    # ea2_indicator_panel,
    # ea3_indicator_panel,
    eb1_indicator_panel_placeholder,
    eb2_indicator_panel_placeholder,
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



    



        


