import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .cohort_text import COHORT_NAMES, COHORT_DESRIPTIONS

# https://panel.holoviz.org/how_to/styling/apply_css.html

class CohortSelector(object):
    # the pane has two versions:
    # - monitoring indicators: the pane is invisible
    # - cohort indicators: the pane is visible
    def __init__(self):
        self._language_code = "en"
        self._default_cohort = "_a_"
        self._cohort_names: dict[str: dict[str: str]] = COHORT_NAMES
        self._cohort_descriptions: dict[str: dict[str: str]] = COHORT_DESRIPTIONS
        self._widget_options = {l_: {v: k for k, v in self._cohort_names[l_].items()} for l_ in self._cohort_names.keys()}
        self.widget = self._get_widget()
        self._pane = self._get_pane()

    def _get_widget(self) -> panel.widgets.RadioButtonGroup:
        _widget_stylesheet = """
        :host(.solid) .bk-btn.bk-btn-default {
            box-shadow: none;
            background: #ffffff00;
            background-color: #ffffff00;
            max-width: 25%;
            color: #555555;
        }
        :host(.solid) .bk-btn-group .bk-btn.bk-btn-default.bk-active {
            box-shadow: none;
            background: rgb(62 125 152);
            background-color: rgb(62 125 152);
            color: #ffffffff;
            border-radius: 8px;
        }
        .bk-btn-group {
            justify-content: space-between;
            padding: 8px;
        }
        """
        widget = panel.widgets.RadioButtonGroup(
            name="Cohort Selector",
            options=self._widget_options[self._language_code],
            value=self._default_cohort,
            css_classes=["cohort-selector"],
            styles={
                # make background and container appearance
                "background": "rgb(211 227 253)",
                "background-color": "rgb(211 227 253)",
                "border-radius": "12px",
            },
            stylesheets=[_widget_stylesheet]
        )
        return widget
    
    def _update_widget(self, language_code: str="en") -> None:
        if language_code not in self._cohort_names.keys():
            language_code = "en"
        self._language_code = language_code
        self.widget.options = self._widget_options[self._language_code]

    def _build_coorte_tooltip_html(self, text: str):
        s_ = """
            <p style="
                color: #888888ff;
                font-size: 0.9em;
                text-align: center;
            ">
        """
        e_ = "</p>"
        text = text.replace("\"", """<span style='color:#707070ff;'><b>""", 1)
        text = text.replace("\"", """</b></span>""", 1)
        return s_ + text + e_
    
    def _get_pane(self) -> panel.viewable.Viewable:
        pane = panel.Column(
            self.widget,
            panel.pane.HTML(
                "" # empty string, but we change it in the get_panel method
            ),
            styles={
                "width": "60%",
                # make  a flex to display stuff in a centered column
                "display": "flex",
                "flex-direction": "column",
                "justify-content": "center",
                "align-items": "center",
                "margin": "auto", # without this the column is not centered
                "margin-top": "15px",
                "margin-bottom": "15px",
            }
        )
        return pane
    
    def _get_empty_pane(self) -> panel.viewable.Viewable:
        return panel.pane.HTML("</hr style='border: 0; margin-top: 25px;'>")
    
    def get_panel(self, language_code: str="en", indicator_type_code: str="_monitoring_", cohort_code: str="_a_") -> panel.viewable.Viewable:
        self._update_widget(language_code)
        self._pane[1].object = self._build_coorte_tooltip_html(self._cohort_descriptions[language_code][cohort_code])
        if indicator_type_code == "_monitoring_":
            return self._get_empty_pane()
        elif indicator_type_code == "_evaluation_":
            return self._pane
        else:
            print("ERROR: indicator_type_code not recognized")
    

if __name__ == "__main__":
    indicator_type_selector_instance = CohortSelector()
    APP = indicator_type_selector_instance.get_panel()
    APP = indicator_type_selector_instance.get_panel("de", "_evaluation_")
    APP.show()
        





# COORTE SELECTOR

def build_coorte_tooltip_html(value: str, text: str):
    s_ = """
        <p style="
            color: #888888ff;
            font-size: 0.9em;
            text-align: center;
        ">
    """
    s_ += "<span style='color:#707070ff;'><b>"+value+"</b></span></br>"
    e_ = "</p>"
    text = text.replace("\"", """<span style='color:#707070ff;'><b>""", 1)
    text = text.replace("\"", """</b></span>""", 1)
    return s_ + text + e_

def update_coorte_html(value):
    return panel.pane.HTML(build_coorte_tooltip_html(value, coorte_explain_dict[display_language][value]))

def build_body_coorte_selector():
    # buttons coorte selector
    coorte_button_options_list = [
        v for v in coorte_explain_dict[display_language].keys()
    ]
    global coorte_radio_group                                       ### THIS IS NOT A GOOD IDEA but i have to make it work
    style_sheet = """
    :host(.solid) .bk-btn.bk-btn-primary.bk-active {
        font-weight: bold;
        background-color: #005587ff;
    }
    """
    coorte_radio_group = panel.widgets.RadioButtonGroup(
        name='coorte selector', 
        options=coorte_button_options_list, 
        value=coorte_button_options_list[0],
        button_type='primary',
        stylesheets=[style_sheet]
    )
    # 
    coorte_selector_row = panel.Column(
        coorte_radio_group,
        panel.bind(update_coorte_html, coorte_radio_group.param.value)
    )
    return coorte_selector_row