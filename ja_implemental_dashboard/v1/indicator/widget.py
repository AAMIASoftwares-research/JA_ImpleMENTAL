import time
import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

from .widget_texts import (
    WIDGET_AGE_NAME_LANGDICT, WIDGET_AGE_ALL_AGES_TITLE,
    WIDGET_GENDER_NAME_LANGDICT, WIDGET_GENDER_OPTIONS_LANGDICT,
    WIDGET_CIVIL_STATUS_NAME_LANGDICT, WIDGET_CIVIL_STATUS_OPTIONS_LANGDICT,
    WIDGET_EDUCATIONAL_LEVEL_NAME_LANGDICT, WIDGET_EDUCATIONAL_LEVEL_OPTIONS_LANGDICT,
    WIDGET_JOB_CONDITION_NAME_LANGDICT, WIDGET_JOB_CONDITION_OPTIONS_LANGDICT
)

class age_widget(object):
    def __init__(self, language_code: str):
        self._language_code = language_code
        # age state
        self.min_age = 0
        self.max_age = 150
        self.min_age_slider = 10
        self.max_age_slider = 90
        self.value = (self.min_age, self.max_age)
        self.last_event_time = time.time()
        # styles
        self.switch_stylesheet = """
            .bar {
                background-color: #bdbdbd;
            }
            :host(.active) .bar {
                background-color: #a6b9d9ff;
            }
            .knob {
                background-color: #918f8f
            }
        """
        # widgets
        self.widget_age_all_names = WIDGET_AGE_ALL_AGES_TITLE
        self.widget_age_all_html = panel.pane.HTML(
            self._get_age_html_title(),
            styles={
                "margin-top": "0px",
                "margin-bottom": "0px",
            }
        )
        self.widget_age_all = panel.widgets.Switch(
            name="All",
            value=True,
            stylesheets=[self.switch_stylesheet]
        )
        self.widget_age_lower_html = panel.pane.HTML(
            f"<p style='margin-bottom: -3px; color: #555555ff; font-size: 0.9em;'> <10</p>",
            styles={
                "margin-top": "0px",
                "margin-bottom": "0px",
            }
        )
        self.widget_age_lower = panel.widgets.Switch(
            name="Lower",
            value=True,
            stylesheets=[self.switch_stylesheet]
        )
        self.widget_age_upper_html = panel.pane.HTML(
            f"<p style='margin-bottom: -3px; color: #555555ff; font-size: 0.9em;'> >90</p>",
            styles={
                "margin-top": "0px",
                "margin-bottom": "0px",
            }
        )
        self.widget_age_upper = panel.widgets.Switch(
            name="Upper",
            value=True,
            stylesheets=[self.switch_stylesheet]
        )
        # slider
        self.slider_stylesheet = """
            .noUi-draggable {
                background-color: #bdbdbd;
            }
            .bk-slider-title {
                font-family: sans-serif;
                font-size: 0.8em;
                color: #555555ff;
            }
        """
        self.widget_age_names = WIDGET_AGE_NAME_LANGDICT
        self.widget_age_value = panel.widgets.IntRangeSlider(
            name=self.widget_age_names[self._language_code],
            start=self.min_age_slider,
            end=self.max_age_slider,
            value=(self.min_age_slider, self.max_age_slider),
            step=1,
            # make it so that it fires the changed signal only when the mouse is released
            callback_throttle=1000,
            stylesheets=[self.slider_stylesheet]
        )
        # callbacks
        self.widget_age_all.param.watch(self._update_age_switches, "value")
        self.widget_age_lower.param.watch(self._update_age_switches, "value")
        self.widget_age_upper.param.watch(self._update_age_switches, "value")
        self.widget_age_value.param.watch(self._update_age_switches, "value")
        # panel
        self._panel_styles = {
            "margin-left": "6px",
            "margin-right": "6px",
        }
        self._panel = panel.Column(
            panel.Row(
                self.widget_age_all_html,
                self.widget_age_lower_html,
                self.widget_age_upper_html,
                styles={
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                    "color": "#555555ff",
                    "font-size": "0.9em",
                }
            ),
            panel.Row(
                self.widget_age_all,
                self.widget_age_lower,
                self.widget_age_upper,
                styles={"margin-top": "2px"}
            ),
            self.widget_age_value,
            styles=self._panel_styles
        )
        # at the end f init, re-initialize the value
        self.value = (self.min_age, self.max_age)

    def _update_age_switches(self, event):
        # rules:
        # - if all is turned on, then all toggles are on and the slider is full
        # - if all is turned off, just the toggles are turned off, the slider remains full
        # - if the toggle all is on and another toggle is turned off, then all is turned off
        # - if the slider is full, and the toggles of lower and upper are on, then all is on
        # - when the toggle for lower or upper is turned on, the respective slider side goes to its maximum
        if time.time() - self.last_event_time < 0.6:
            return
        self.last_event_time = time.time()
        if event.obj.name == "Lower":
            if event.new:
                self.value = (self.min_age, self.value[1])
                self.widget_age_value.value = (self.min_age_slider, self.widget_age_value.value[1])
                if self.widget_age_upper.value:
                    self.widget_age_all.value = True
            else:
                self.value = (self.widget_age_value.value[0], self.value[1])
                if self.widget_age_all.value:
                    self.widget_age_all.value = False
        if event.obj.name == "Upper":
            if event.new:
                self.value = (self.value[0], self.max_age)
                self.widget_age_value.value = (self.widget_age_value.value[0], self.max_age_slider)
                if self.widget_age_lower.value:
                    self.widget_age_all.value = True
            else:
                self.value = (self.value[0], self.widget_age_value.value[1])
                if self.widget_age_all.value:
                    self.widget_age_all.value = False
        if event.obj.name == "All":
            if event.new:
                # The toggle has been swithed on
                self.value = (self.min_age, self.max_age)
                self.widget_age_value.value = (self.min_age_slider, self.max_age_slider)
                self.widget_age_lower.value = True
                self.widget_age_upper.value = True
            else:
                # The toggle has been swithed off
                self.value = (self.min_age_slider, self.max_age_slider)
                self.widget_age_lower.value = False
                self.widget_age_upper.value = False
        if event.obj.name == "Age":
            # value logic
            self.value = event.new
            # toggles logic
            if self.widget_age_all.value:
                self.widget_age_all.value = False
            if event.new[0] != self.min_age_slider:
                self.widget_age_lower.value = False
            if event.new[1] != self.max_age_slider:
                self.widget_age_upper.value = False

    def _get_age_html_title(self) -> str:
        return f"<p style='margin-bottom: -3px; color: #555555ff; font-size: 0.9em;'>{self.widget_age_all_names[self._language_code]}</p>"
    
    def update_language(self, language_code: str) -> None:
        if language_code not in WIDGET_AGE_NAME_LANGDICT.keys():
            raise ValueError("Language code not recognized:", language_code)
        self._language_code = language_code
        self.widget_age_all_html.object = self._get_age_html_title()
        self.widget_age_value.name = self.widget_age_names[self._language_code]

    def get_panel(self, language_code: str) -> panel.Column:
        if language_code != self._language_code:
            self.update_language(language_code)
        return self._panel


class indicator_widgets(object):
    def __init__(self, language_code: str):
        self._language_code = language_code
        # all widgets
        self._selector_stylesheet = """
            select:not([multiple]).bk-input, select:not([size]).bk-input {
                border: 1.2px solid rgb(0 0 0 / 0%);
                background-color: #ffffff;
                font-style: normal;
                font-weight: 600;
                font-family: sans-serif;
                font-size: 1.1em;
                color: #3e7d98ff;
                orientation: ltr;
                cursor: pointer;
                background-image: url('data:image/svg+xml;utf8,<svg version="1.1" viewBox="0 0 25 20" xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 25,0 12.5,20 Z" fill="white" /></svg>')
            }
            option {
                background: #000000ff;
                background-color: #f0f0f0ff;
                font-family: sans-serif;
                font-size: 0.9em;
                font-weight: 400;
                color: #555555ff;
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
        # widgets - age
        self.widget_age_instance = age_widget(self._language_code)
        # widgets - gender
        self._gender_widget_names = WIDGET_GENDER_NAME_LANGDICT
        self._gender_widget_options = WIDGET_GENDER_OPTIONS_LANGDICT
        self._gender_widget_styles = {}
        self.widget_gender = self._get_gender_widget()
        # widgets - civil status
        self._civil_status_widget_names = WIDGET_CIVIL_STATUS_NAME_LANGDICT
        self._civil_status_widget_options = WIDGET_CIVIL_STATUS_OPTIONS_LANGDICT
        self._civil_status_widget_styles = {}
        self.widget_civil_status = self._get_widget_civil_status()
        # widgets - educational level
        self._educational_level_widget_names = WIDGET_EDUCATIONAL_LEVEL_NAME_LANGDICT
        self._educational_level_widget_options = WIDGET_EDUCATIONAL_LEVEL_OPTIONS_LANGDICT
        self._educational_level_widget_styles = {}
        self.widget_educational_level = self._get_widget_educational_level()
        # widgets - job condition
        self._job_condition_widget_names = WIDGET_JOB_CONDITION_NAME_LANGDICT
        self._job_condition_widget_options = WIDGET_JOB_CONDITION_OPTIONS_LANGDICT
        self._job_condition_widget_styles = {}
        self.widget_job_condition = self._get_widget_job_condition()
        # panel
        self._panel_styles = {
            "background-color": "#d3e3fd",
            "padding": "10px",
            "border-radius": "10px",
            "border": "1px solid #a0a0a0",
            "max-width": "250px",
            "margin-right": "30px",
        }
        self._panel_stylesheet = ""
    
    def _get_gender_widget(self) -> panel.widgets.Select:
        widget = panel.widgets.Select(
            options={v: k for k, v in self._gender_widget_options[self._language_code].items()},
            value="A",
            name=self._gender_widget_names[self._language_code],
            styles=self._gender_widget_styles,
            stylesheets=[self._selector_stylesheet]
        )
        return widget
    
    def _update_language_gender_widget(self) -> None:
        self.widget_gender.options = {
            v: k for k, v in self._gender_widget_options[self._language_code].items()
        }
        self.widget_gender.name = self._gender_widget_names[self._language_code]

    def _get_widget_civil_status(self) -> panel.widgets.Select:
        widget = panel.widgets.Select(
            options={v: k for k, v in self._civil_status_widget_options[self._language_code].items()},
            value="All",
            name=self._civil_status_widget_names[self._language_code],
            styles=self._civil_status_widget_styles,
            stylesheets=[self._selector_stylesheet]
        )
        return widget
    
    def _update_language_civil_status_widget(self) -> None:
        self.widget_civil_status.options = {
            v: k for k, v in self._civil_status_widget_options[self._language_code].items()
        }
        self.widget_civil_status.name = self._civil_status_widget_names[self._language_code]

    def _get_widget_educational_level(self) -> panel.widgets.Select:
        widget = panel.widgets.Select(
            options={v: k for k, v in self._educational_level_widget_options[self._language_code].items()},
            value="All",
            name=self._educational_level_widget_names[self._language_code],
            styles=self._educational_level_widget_styles,
            stylesheets=[self._selector_stylesheet]
        )
        return widget
    
    def _update_language_educational_level_widget(self) -> None:
        self.widget_educational_level.options = {
            v: k for k, v in self._educational_level_widget_options[self._language_code].items()
        }
        self.widget_educational_level.name = self._educational_level_widget_names[self._language_code]

    def _get_widget_job_condition(self) -> panel.widgets.Select:
        widget = panel.widgets.Select(
            options={v: k for k, v in self._job_condition_widget_options[self._language_code].items()},
            value="All",
            name=self._job_condition_widget_names[self._language_code],
            styles=self._job_condition_widget_styles,
            stylesheets=[self._selector_stylesheet]
        )
        return widget

    def _update_language_job_condition_widget(self) -> None:
        self.widget_job_condition.options = {
            v: k for k, v in self._job_condition_widget_options[self._language_code].items()
        }
        self.widget_job_condition.name = self._job_condition_widget_names[self._language_code]

    def get_panel(self, language_code: str) -> panel.Column:
        # update widgets language
        if language_code not in self._gender_widget_names.keys():
            raise ValueError("Language code not recognized:", language_code)
        self._language_code = language_code
        self._update_language_gender_widget()
        self._update_language_civil_status_widget()
        self._update_language_educational_level_widget()
        self._update_language_job_condition_widget()
        # make the panel
        pane = panel.Column(
            self.widget_age_instance.get_panel(language_code=language_code),
            self.widget_gender,
            self.widget_civil_status,
            self.widget_educational_level,
            self.widget_job_condition,
            styles=self._panel_styles,
            stylesheets=[self._panel_stylesheet]
        )
        return pane


if __name__ == "__main__":
    widgets_instance = indicator_widgets(language_code="en")
    app = widgets_instance.get_panel(language_code="it")
    app.show()