import os, sys, time

import panel
from ._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .language_selector import LanguageSelector
from .header import Header
from .footer import Footer


if __name__ == "__main__":

    language_selector_instance = LanguageSelector()
    header_instance = Header()
    footer_instance = Footer()
    APP = panel.Column(
        language_selector_instance.get_panel(),
        panel.bind(header_instance.get_panel, language_selector_instance.widget),
        panel.bind(footer_instance.get_panel, language_selector_instance.widget)
    )
    APP.show()