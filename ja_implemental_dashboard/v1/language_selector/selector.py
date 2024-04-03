import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .text import LANGUAGE_LANG_DICT, FLAGS_HTML_EMBEDDING_DICT

class LanguageSelector(object):
    def __init__(self) -> None:
        # Widget
        self._languages = LANGUAGE_LANG_DICT
        self._default_language = "en"
        self._display_language = self._default_language
        self.widget_styles = {
            "border-radius": "3px",
            "margin-top": "0",
            "padding-top": "0",
            "background": "#00000020"
        }
        self.widget_width = 110
        self.widget = panel.widgets.Select(
            value=self._display_language,
            options={self._languages[key]: key for key in self._languages.keys()},
            width=self.widget_width,
            styles=self.widget_styles
        )
        # Container
        self._panel_styles = {
            "position": "absolute",
            "margin-top": "15px",
            "margin-left": "calc(100vw - 190px)",
            "background": "#ffffffb3",
            "border-radius": "5px",
            "max-width": "130px",
            "z-index": "1000",
            "cursor": "pointer"
        }
        self._panel_title_text_color = "#333333"
        self._panel = self.get_panel()
    
    def _make_name_html(self):
        text = self._languages[self._display_language]
        html = """<div style="
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 1px;
                padding: 0px 0px 0px 0px;
                font-size: 0.9em;
                font-weight: 600;
                font-family: sans-serif;
                color: """ + self._panel_title_text_color + """;
            ">
            """ + FLAGS_HTML_EMBEDDING_DICT[self._display_language] + """
            <p style="
            margin-block-start: 0;
            margin-block-end: 0;
            padding-left: 5px;">""" + text + """</p>
            </div>"""
        return panel.pane.HTML(html)
    
    def update_language(self, language):
        if language not in self._languages.keys():
            raise ValueError("Invalid language code for language selector. Available language codes: " + str(self._languages.keys()), ", got language code: ", language)
        self._display_language = language
        # to comply with the panel.bind() behaviour, we make this function (and this only)
        # return the title of the panel (the html part)
        return self._make_name_html()
        
    def get_panel(self) -> panel.viewable.Viewable:
        # and now, we return the panel
        language_selector_column = panel.Column(
            panel.bind(self.update_language, self.widget),
            self.widget,
            styles=self._panel_styles
        )
        self._panel = language_selector_column
        return self._panel
    

    


if __name__ == "__main__":
    language_selector_instance = LanguageSelector()
    APP = language_selector_instance.get_panel()
    APP.show()




