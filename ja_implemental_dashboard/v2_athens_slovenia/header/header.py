import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .text import TITLE_TEXT_LANG_DICT, HOME_BUTTON_TEXT_LANG_DICT, DASHBOARD_BUTTON_TEXT_LANG_DICT

class Header(object):
    def __init__(self):
        self._language_code = "en"
        self._title_texts = TITLE_TEXT_LANG_DICT
        self._home_button_texts = HOME_BUTTON_TEXT_LANG_DICT
        self._dashboard_button_texts = DASHBOARD_BUTTON_TEXT_LANG_DICT
        self._background_image_url = "https://implemental.files.wordpress.com/2021/11/2000_podloga-s-logo.jpg"
        self._homepage_url = "https://ja-implemental.eu/"
        self._panel_styles = {
            "width": "calc(100vw - 17px)",
            "margin": "0",
            "padding": "0"
        }
        self._panels = self._get_panel_all_alnguages()

    def _get_panel_all_alnguages(self)  -> dict[str: panel.viewable.Viewable]:
        panels = {}
        for language_code in self._title_texts.keys():
            title_text = self._title_texts[language_code]
            home_button_text = self._home_button_texts[language_code]
            dashboard_button_text = self._dashboard_button_texts[language_code]
            header = panel.panel(
                """
                <div class="header-container-implemental" style="
                    display: flex;
                    flex-direction: row;
                    justify-content: space-evenly;
                    align-items: center;
                    width: calc(100vw - 17px);
                    max-height: 311px;
                    min-height: 310px;
                    padding: 0;
                    margin: 0;
                    background: url('""" + self._background_image_url + """');
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-position: 50%;
                    box-sizing: border-box;
                    border-radius: 0px 0px 16px 16px;
                ">
                    <div style="
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                        height: 100%;
                    ">
                        <h1 style="
                            margin-right: 1.5em;
                            font-style: normal;
                            font-weight: 600;
                            font-family: sans-serif;
                            font-size: 1.3em;
                            direction: ltr;
                            text-align: center;
                            color: #333333;
                            ">
                            """ + title_text + """
                        </h1>
                        <div style="
                            display: flex;
                            flex-direction: row;
                            justify-content: center;
                            align-items: center;
                            width: 100%;
                            height: 100%;
                            margin-top: 1.2em;
                        ">
                            <a href=" """ + self._homepage_url +""" " target="_blank" style="text-decoration: none;color: inherit;">
                                <button style="
                                    margin-right: 1em;
                                    color: #ffffff;
                                    background-color: #3e7d98;
                                    border: solid 3px #3e7d98;
                                    border-radius: 500px;
                                    padding: 0.5em 1em;
                                    font-style: normal;
                                    font-weight: 800;
                                    font-family: sans-serif;
                                    font-size: 1.4em;
                                    direction: ltr;
                                    text-align: center;
                                    cursor: pointer;
                                    transition: background-color .125s ease-in;
                                ">
                                    """ + home_button_text + """
                                </button>
                            </a>
                            <button onclick="window.scrollTo({ top: 312, behavior: 'smooth' })" style="
                                margin-left: 1em;
                                color: #3e7d98;
                                background-color: #ffffff;
                                border: solid 3px #ffffff;
                                border-radius: 500px;
                                padding: 0.5em 1em;
                                font-style: normal;
                                font-weight: 800;
                                font-family: sans-serif;
                                font-size: 1.4em;
                                direction: ltr;
                                text-align: center;
                                cursor: pointer;
                                transition: background-color .125s ease-in;
                            ">
                                """ + dashboard_button_text + """
                            </button>
                        </div>
                    </div>
                </div>
                """,
                styles=self._panel_styles
            )
            panels[language_code] = header
        return panels
        
    def get_panel(self, language_code: str="en") -> panel.viewable.Viewable:
        # update language internal state
        if language_code not in self._title_texts.keys():
            raise ValueError("Invalid language code for header title. Available language codes: " + str(self._title_texts.keys()))
        if language_code not in self._home_button_texts.keys():
            raise ValueError("Invalid language code for header home button. Available language codes: " + str(self._home_button_texts.keys()))
        if language_code not in self._dashboard_button_texts.keys():
            raise ValueError("Invalid language code for header dashboard button. Available language codes: " + str(self._dashboard_button_texts.keys()))
        self._language_code = language_code
        # return the panel
        return self._panels[self._language_code]
    

if __name__ == "__main__":
    # TEST
    header = Header()
    header.get_panel("it").show()
        

