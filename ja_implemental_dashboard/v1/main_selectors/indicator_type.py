import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .indicator_type_text import IT_LANG_DICT

# https://panel.holoviz.org/how_to/styling/apply_css.html

class IndicatorTypeSelector(object):
    def __init__(self):
        self._language_code = "en"
        self._default_indicator_type_code = "_monitoring_"
        self._indicator_types: dict[str: dict[str: str]] = IT_LANG_DICT
        self._widget_stylesheets = """
            :host(.solid) .bk-btn.bk-btn-default {
                # the inactive buttons
                background: #ffffffff;
                background-color: rgb(211 227 253);
                color: #909090ff;
                box-shadow: none;
                #border-bottom-width: 4px;
                #border-bottom-color: #909090ff;
                border-radius: 0;
                font-size: 1.2em;
                font-weight: 600;
                cursor: default;
            }
            :host(.solid) .bk-btn-group .bk-btn.bk-btn-default.bk-active {
                # the active button
                background: #ffffffff;
                background-color: #ffffffff;
                color: #3e7d98ff;
                box-shadow: none;
                border-radius: 8px 8px 0px 0px; # tl, tr, br, bl
            }
        """
        self._widget_options = {l_: {v: k for k, v in self._indicator_types[l_].items()} for l_ in self._indicator_types.keys()}
        self.widget = self._get_widget()
        self._pane = self._get_pane()

    def _get_widget(self) -> panel.widgets.RadioButtonGroup:
        widget = panel.widgets.RadioButtonGroup(
            name="Indicator type",
            options=self._widget_options[self._language_code],
            value=self._default_indicator_type_code,
            width=300,
            margin=(0, 0, 0, 0),
            align="start",
            css_classes=["indicator-type-selector"],
            styles={"margin-left": "20px"},
            stylesheets=[self._widget_stylesheets]
        )
        return widget
    
    def _update_widget(self, language_code: str="en") -> None:
        if language_code not in self._indicator_types.keys():
            language_code = "en"
        self._language_code = language_code
        self.widget.options = self._widget_options[self._language_code]
    
    def _get_pane(self) -> panel.viewable.Viewable:
        pane = panel.Column(
            self.widget,
            styles={
                "background": "rgb(211 227 253)",
                "background-color": "rgb(211 227 253)",
                "padding-top": "10px",
                "margin-top": "-10px",
                "border-radius": "0px 0px 16px 16px",
            }            
        )
        return pane
    
    def get_panel(self, language_code: str="en") -> panel.viewable.Viewable:
        self._update_widget(language_code)
        return self._pane
    

if __name__ == "__main__":
    indicator_type_selector_instance = IndicatorTypeSelector()
    APP = indicator_type_selector_instance.get_panel()
    indicator_type_selector_instance._update_widget("it")
    APP = indicator_type_selector_instance.get_panel("fr")
    APP.show()
        
