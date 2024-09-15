import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .disease_text import DS_DEFAULT_TITLE_MESSAGE, DS_TITLE

class DiseaseSelector(object):
    def __init__(self):
        # title
        self._language_code = "en"
        self._disease_code = "_all_"
        self._titles = DS_TITLE
        self._title_styles = {
            "width": "auto",
            "margin": "auto",
            "margin-left": "25px",
        }
        self._title_panes = self._get_title_panes()
        # widget
        self._default_widget_messages = DS_DEFAULT_TITLE_MESSAGE
        self._widget_width = 300
        self._widget_max_width = 300
        self._widget_min_width = 150
        self._widget_styles = {
            "margin-right": "25px"
        }
        self._widget_stylesheet = """
            select:not([multiple]).bk-input, select:not([size]).bk-input {
                border: 1.2px solid rgb(0 0 0 / 0%);
                background-color: #3e7d98ff;
                font-style: normal;
                font-weight: 600;
                font-family: sans-serif;
                font-size: 1.1em;
                color: #ffffff;
                orientation: ltr;
                cursor: pointer;
                background-image: url('data:image/svg+xml;utf8,<svg version="1.1" viewBox="0 0 25 20" xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 25,0 12.5,20 Z" fill="white" /></svg>')
            }
            option {
                background: #ffffff;
                background-color: #ffffff;
                font-style: normal;
                font-weight: 600;
                font-family: sans-serif;
                font-size: 0.95em;
                color: #3e7d98ff;
                orientation: ltr;
                cursor: pointer;
            }
            label {
                font-family: sans-serif;
                font-size: 0.9em;
                font-weight: 400;
                color: #555555ff;
                padding-left: 10px;
            }
        """
        self._widget_options = {l_: {v: k for k, v in self._titles[l_].items()} for l_ in self._titles.keys()}
        self.widget = self._get_widget()
        # whole element
        self._panel_flex_direction = "row"
        self._panel_flex_wrap = "nowrap"
        self._panel_align_content = "center"
        self._panel_justify_content = "space-around"
        self._panel_align_items = "center"
        self._panel_styles = {
            "width": "100%",
            "margin": "auto",
            "margin-top": "15px",
            "padding-top": "0px",
            "margin-bottom": "5px",
            "background": "rgb(211 227 253)",
            "border-radius": "16px 16px 0px 0px"
        }
    
    def _get_title_panes(self) -> dict[str: dict[str: panel.pane.HTML]]:
        panels = {k: {} for k in self._titles.keys()}
        for _lang in self._titles.keys():
            for _disease in self._titles[_lang].keys():
                pan = panel.pane.HTML(
                    """<h1 styles="width: auto; color: #555555;">"""+self._titles[_lang][_disease]+"""</h1>""",
                    styles=self._title_styles
                )
                panels[_lang][_disease] = pan
        return panels
    
    def _get_widget(self) -> panel.widgets.Select:
        widget = panel.widgets.Select(
            name=self._default_widget_messages[self._language_code],
            options=self._widget_options[self._language_code],
            value=self._disease_code,
            width=self._widget_width,
            max_width=self._widget_max_width,
            min_width=self._widget_min_width,
            styles=self._widget_styles,
            stylesheets=[self._widget_stylesheet]
        )
        # and an on_change event that conect to the loading_visible javascript function
        return widget
    
    def _update_widget(self, language_code: str="en", disease_code: str="_all_") -> None:
        # making a new widget does not work because it gets decoupled
        # from the original one and the binding does not work anymore
        # -> we need to update the existing widget
        # -> This works perfect
        self.widget.name = self._default_widget_messages[language_code]
        self.widget.options = self._widget_options[language_code]
        self.widget.value = disease_code

    def get_panel(self, language_code, disease_code) -> panel.FlexBox:
        self._language_code = language_code
        self._disease_code = disease_code
        self._update_widget(language_code, disease_code)
        pane = panel.FlexBox(
            self._title_panes[self._language_code][disease_code],
            self.widget,
            flex_direction=self._panel_flex_direction,
            flex_wrap=self._panel_flex_wrap,
            align_content=self._panel_align_content,
            justify_content=self._panel_justify_content,
            align_items=self._panel_align_items,
            styles=self._panel_styles
        )
        return pane
    

if __name__ == "__main__":
    def make_html_prova(disease_code):
        print(disease_code)
        return panel.pane.HTML("""<h2>Disease code: """+disease_code+"""</h2>""")
    disease_selector_instance = DiseaseSelector()
    APP = panel.Column(
        disease_selector_instance.get_panel("en", "_all_"),
        panel.bind(make_html_prova, disease_selector_instance.widget)
    )
    APP.show()







