import os
from os.path import normpath

LANGUAGE_LANG_DICT = {
    "en": "English",
    "it": "Italiano",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "pt": "Português",
}

project_folder = "C:/Users/lecca/Desktop/AAMIASoftwares-research/JA_ImpleMENTAL/"
flags_iso_relative_path = "assets/flags_GoSquared/flags/flags-iso/shiny/64/"
online_path = "https://raw.githubusercontent.com/gosquared/flags/master/flags/flags-iso/shiny/64/"

flag_names_dict = {
    "en": "GB",
    "it": "IT",
    "de": "DE",
    "fr": "FR",
    "es": "ES",
    "pt": "PT"
}

FLAGS_IMAGES_URL_DICT = {
    k: online_path+flag_names_dict[k] + ".png" for k in LANGUAGE_LANG_DICT.keys()
}

FLAGS_HTML_EMBEDDING_DICT = {
    k: f'<img src="{FLAGS_IMAGES_URL_DICT[k]}" style="width: 1.3em; height: 1.3em;">' for k in LANGUAGE_LANG_DICT.keys()
}