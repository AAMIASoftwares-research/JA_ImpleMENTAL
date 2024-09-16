import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .text import FOOTER_TEXT_LANG_DICT

class Footer(object):
    def __init__(self):
        self._language_code = "en"
        self._texts = FOOTER_TEXT_LANG_DICT
        self._eu_image_url = "https://implemental.files.wordpress.com/2022/09/en-co-funded-by-the-eu_pos.png?w=300"
        self._panel_styles = {
            "margin": "0",
            "padding": "0",
            "position": "fixed",
            "bottom": "0",
            "z-index": "9990"
            # "z-index" makes sure that it always stays on top of everything else in the web page
        }
        self._panels = self._get_panel_all_languages()

    def _get_panel_all_languages(self)  -> panel.viewable.Viewable:
        panels = {}
        for language_code in self._texts.keys():
            footer_main_text = self._texts[language_code]
            footer = panel.pane.HTML(
                """
                <footer style="
                        z-index: 2147483646;
                        position: absolute; 
                        bottom: 0; 
                        width: calc(100vw - 17px); 
                        margin-left: 0px;
                        padding: 5px 0; 
                        background-color: #e9ecef;
                        border-radius: 16px 16px 0px 0px;
                        border: solid 1px #555555;
                        margin-bottom: -2px;
                ">
                    <div style="
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                        ">
                        <img src=" """ + self._eu_image_url + """ " alt="Cofunded by the European Union" style="
                                width: 150px; 
                                height: auto; 
                                margin-right: 20px;
                                padding-left: 20px;
                                min-width: 150px;
                                max-width: 200px;
                        ">
                        <p style="
                                text-align: left; 
                                line-height: 1.5;
                                padding-right: 20px;
                                font-size: 0.85em;
                                color: #546e7a;
                        ">""" + footer_main_text + """</p>
                    </div>
                </footer>
                """,
                styles=self._panel_styles
            )
            panels[language_code] = footer
        return panels
    
    def get_panel(self, language_code: str="en") -> panel.viewable.Viewable:
        if language_code not in self._texts.keys():
            raise ValueError("Invalid language code for footer text. Available language codes: " + str(self._texts.keys()))
        self._language_code = language_code
        return self._panels[self._language_code]
    

if __name__ == "__main__":
    # TEST
    footer = Footer()
    footer.get_panel("pt").show()
        
