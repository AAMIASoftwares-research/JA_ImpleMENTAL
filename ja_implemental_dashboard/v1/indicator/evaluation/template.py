import numpy
import pandas
import panel
from ..._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)
import holoviews
holoviews.extension('bokeh')

from ...database.database import DISEASE_CODE_TO_DB_CODE, COHORT_CODE_TO_DB_CODE
from ..logic_utilities import clean_indicator_getter_input, stratify_demographics

