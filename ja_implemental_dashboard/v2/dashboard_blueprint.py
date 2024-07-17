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
    # THIS IS HOW IT WORKS
    #
    # 1. Create an instance of the LanguageSelector class
    #    This has to be the first element in the final app.
    #    This elements always stays on top of the other elements,
    #    so it can be put first no problem.
    # 2. Create all other instances
    #    These are the other elements of the app.
    # 3. Create the final app
    #    You should use panel.bind to bind the update method of the app elements
    #    to the widget of the language selector (and any other widget).
    #    In this way, every time the language changes, the update method of the app elements
    #    is called with the new language as argument.
    #    So, the get_panel method of the app elements should accept a language argument,
    #    as well as any other needed argument for other binds, and return the updated panel.
    #
    # Advice:
    #    To make it all faster, create all the app elements in all the available languages,
    #    so then you can serve them dynamically without having to create them every time.

    language_selector_instance = LanguageSelector()
    header_instance = Header()
    footer_instance = Footer()
    APP = panel.Column(
        language_selector_instance.get_panel(),
        panel.bind(header_instance.get_panel, language_selector_instance.widget),
        panel.bind(footer_instance.get_panel, language_selector_instance.widget)
    )
    APP.show()