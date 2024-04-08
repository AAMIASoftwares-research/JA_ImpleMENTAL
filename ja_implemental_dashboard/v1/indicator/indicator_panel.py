import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from panel.theme import Material

class EmptyPanel(object):
    # This class is needed because, for some unknown reason,
    # if the number of elements in the dispatcher monitoring and evaluation
    # lists is not the same, the dashboard will not display some of the panels
    def __init__(self, indicator_type):
        self._indicator_type = indicator_type
        self._pane = panel.pane.HTML("<br/>")

    def get_panel(self, **kwargs):
        return self._pane


class IndicatorPanel(object):
    """
    This class contains the logic for displaying the whole indicator panel
    Indicator is composed of:
    - Indicator Code (es MA1, MB3, EA1, EC4, ...)
    - indicator name
    - indicator short description
    - tabs
      each indicator can have multiple tabs, in the tabs can be
      displayed literally anything
      tabs is a list of objects that are indicator specific classes that have the
      get_panel method, that is called by this class to build the panel
    """
    def __init__(self, monitoring_or_evaluation: str, indicator_code: str, indicator_name: dict, indicator_short_description: dict, tabs: list[object], tab_names_langdict: dict[str:list[str]]):
        self._indicator_type = monitoring_or_evaluation
        self._indicator_code = indicator_code
        self._indicator_names = indicator_name
        self._indicator_short_descriptions = indicator_short_description
        self._title_row_style = {"margin": "0px"}
        self._title_row_stylesheet = ""
        # titles (all languages)
        self._title_rows = self._get_title_rows()
        # tabs are created dynamically by the get_panel method
        # here's the list of tab contents that have the method to
        # get the panel
        self._tabs = tabs
        self._tab_names = tab_names_langdict
        self._tabs_active_tab_index: int = 0
        self._tabs_styles = {"margin": "0px"}
        self._tabs_stylesheet = """
            :host(.bk-above) .bk-header {
                border-bottom: none;
                background: #eceff7;
                max-width: fit-content;
                padding: 8px;
                border-radius: 12px;
            }
            :host(.bk-above) .bk-header .bk-tab {
                border-bottom: none;
                background-color: #00000000;
                background: #00000000;
                padding: 6px 12px 6px 12px;
            }
            :host(.bk-above) .bk-header .bk-tab.bk-active {
                border-bottom: none;
                border-radius: 8px;
                background-color: rgb(62 125 152);
                background: rgb(62 125 152);
                color: #ffffffff;
                padding: 6px 12px 6px 12px;

            }
        """
        # pane element
        self._pane_styles = {"margin": "0px", "margin-left": "30px",}
        self._pane_stylesheet = {}

    def _get_title_rows(self):
        title_rows = {k : {} for k in self._indicator_names.keys()}
        for lang in self._indicator_names.keys():
            title_rows[lang] = panel.pane.HTML(
                f"""<h2 style='
                    margin: 0px;
                    font-weight: 600;
                    font-size: 1.05em;
                    color: #555555;
                '>
                {self._indicator_code} - {self._indicator_names[lang]}
                </h2>
                <p style='
                    margin: 0px;
                    margin-top: 2px;
                    margin-left: 8px;
                    margin-bottom: 6px;
                    font-size: 0.85em;
                    color: #777777;
                '>{self._indicator_short_descriptions[lang]}</p>
                """,
                styles=self._title_row_style,
                stylesheets=[self._title_row_stylesheet]
            )
        return title_rows
    
    def _set_active_tab_index(self, event):
        if event.name == "active":
            self._tabs_active_tab_index = event.new
    
    def _get_tabs_element_dynamic(self, language_code, disease_code, cohort_code: str|None=None):
        tabs_element = panel.Tabs(
            *[
                (tn, t.get_panel(language_code=language_code, disease_code=disease_code, cohort_code=cohort_code)) 
                for tn, t in zip(self._tab_names[language_code], self._tabs)
            ],
            tabs_location="above",
            active=self._tabs_active_tab_index,
            design=Material,
            styles=self._tabs_styles,
            stylesheets=[self._tabs_stylesheet]
        )
        # connect here since we create it dynamically
        tabs_element.param.watch(self._set_active_tab_index, "active")
        return tabs_element
    
    def get_panel(self, **kwargs):
        # expected kwargs:
        # language_code, disease_code, cohort_code (not mandatory)
        lc = kwargs.get("language_code", "en")
        dc = kwargs.get("disease_code", "_depression_")
        cc = kwargs.get("cohort_code", None)
        if self._indicator_type == "_evaluation_":
            if cc is None:
                raise ValueError("Cohort code is mandatory for evaluation indicators")
        title_row = self._title_rows[lc]
        tabs_element = self._get_tabs_element_dynamic(language_code=lc, disease_code=dc, cohort_code=cc)
        pane = panel.Column(
            title_row,
            tabs_element,
            styles=self._pane_styles,
            stylesheets=[self._pane_stylesheet]
        )
        return pane
    
