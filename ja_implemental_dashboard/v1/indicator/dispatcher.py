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
        # make the two lists the same length
        if len(self._monitoring_panel_classes) > len(self._evaluation_panel_classes):
            self._evaluation_panel_classes.extend(
                [
                    EmptyPanel("_evaluation_") 
                    for _ in range(len(self._monitoring_panel_classes) - len(self._evaluation_panel_classes))
                ]
            )
        elif len(self._monitoring_panel_classes) < len(self._evaluation_panel_classes):
            self._monitoring_panel_classes.extend(
                [
                    EmptyPanel("_monitoring_") 
                    for _ in range(len(self._evaluation_panel_classes) - len(self._monitoring_panel_classes))
                ]
            )
        # pane styles
        self._pane_styles = {
            "margin": "0px",
            "margin-top": "20px",
            "margin-left": "10px"
        }
        self._pane_stylesheet = ""

    def get_panel(self, language_code, disease_code, indicator_type_code, cohort_code):
        # ALL DISEASES
        if disease_code == "_all_":
            pane = panel.Column(
                panel.pane.HTML("<h3>Choose a disease</h3>"),
                styles={
                    "margin": "auto",
                    # align content horizontaly in the center
                    "display": "flex",
                    "justify-content": "center",
                    "align-items": "center",
                },
                stylesheets=[self._pane_stylesheet]
            )
            return pane
        # SELECTED DISEASE
        if indicator_type_code == "_monitoring_":
            print("\n\n\nmonitoring panel classes: ", self._monitoring_panel_classes)
            panes_list = [
                p.get_panel(language_code=language_code, disease_code=disease_code) 
                for p in self._monitoring_panel_classes 
                if p._indicator_type == "_monitoring_"
            ]
        elif indicator_type_code == "_evaluation_":
            print("\n\n\nevaluation panel classes: ", self._evaluation_panel_classes)
            panes_list = [
                p.get_panel(language_code=language_code, disease_code=disease_code, cohort_code=cohort_code)
                for p in self._evaluation_panel_classes
                if p._indicator_type == "_evaluation_"
            ]
        else:
            raise ValueError("Indicator type not recognized:", indicator_type_code)
        pane = panel.Column(
            *panes_list,
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        print("\n\n\ndispatcher get_panel called: ", language_code, disease_code, indicator_type_code, cohort_code)
        print(pane, len(pane.objects))
        return pane








# Create here the instances of the panels

############
#######
#######
    
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
    monitoring_or_evaluation="_evaluation_",
    indicator_code="EA2",
    indicator_name={"en": "Another indicator - <span style='font-weight: bold;'>without styling</span>", "it": "Nome indicatore"},
    indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
    tabs=panes_classes,
    tab_names_langdict={"en": panes_names, "it": panes_names}
)

indicator_panel_2 = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code="EA2",
    indicator_name={"en": "Another indicator - <span style='font-weight: bold;'>without styling</span>", "it": "Nome indicatore"},
    indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
    tabs=panes_classes,
    tab_names_langdict={"en": panes_names, "it": panes_names}
)

indicator_panel_3 = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code="EA3",
    indicator_name={"en": "Another indicator - <span style='font-weight: bold;'>without styling</span>", "it": "Nome indicatore"},
    indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
    tabs=panes_classes,
    tab_names_langdict={"en": panes_names, "it": panes_names}
)

indicator_panel_4 = IndicatorPanel(
    monitoring_or_evaluation="_evaluation_",
    indicator_code="EA4",
    indicator_name={"en": "Another indicator - <span style='font-weight: bold;'>without styling</span>", "it": "Nome indicatore"},
    indicator_short_description={"en": "Short description", "it": "Descrizione breve"},
    tabs=panes_classes,
    tab_names_langdict={"en": panes_names, "it": panes_names}
)





###########
##########
##########

# Load database here
#####################
import numpy
import pandas
from ..database.database import FILES_FOLDER, DATABASE_FILENAMES_DICT, read_databases, preprocess_demographics_database, preprocess_interventions_database, preprocess_cohorts_database

db = read_databases(DATABASE_FILENAMES_DICT, FILES_FOLDER)
db["demographics"] = preprocess_demographics_database(db["demographics"])
db["interventions"] = preprocess_interventions_database(db["interventions"])
db["cohorts"] = preprocess_cohorts_database(db["cohorts"])

# - a little data augmentation to better display the dashboard
cohorts_rand = db["cohorts"].copy(deep=True)
cohorts_rand["YEAR_ENTRY"] = pandas.Series(numpy.random.randint(2013, 2016, cohorts_rand.shape[0]), index=cohorts_rand.index)
__DB__ = {
    "demographics": db["demographics"],
    "diagnoses": db["diagnoses"],
    "pharma": db["pharma"],
    "interventions": db["interventions"],
    "physical_exams": db["physical_exams"],
    "cohorts": cohorts_rand
}


# Make all indicator panels to be displayed in the dashboard

from .monitoring.a1 import (
    ma1_code, ma1_name_langdict, ma1_short_desription_langdict,
    ma1_tab_names_langdict,
    ma1_tab0, ma1_tab1
)
ma1_tab0_instance = ma1_tab0(__DB__)
ma1_tab1_instance = ma1_tab1()
ma1_indicator_panel = indicator_panel_1 = IndicatorPanel(
    monitoring_or_evaluation="_monitoring_",
    indicator_code=ma1_code,
    indicator_name=ma1_name_langdict,
    indicator_short_description=ma1_short_desription_langdict,
    tabs=[ma1_tab0_instance, ma1_tab1_instance],
    tab_names_langdict=ma1_tab_names_langdict
)





# This is to be imported into the main dashboard

dispatcher_instance = Dispatcher(
    monitoring_panel_classes=[ma1_indicator_panel],
    evaluation_panel_classes=[indicator_panel_1, indicator_panel_2, indicator_panel_3, indicator_panel_4]
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



    



        


