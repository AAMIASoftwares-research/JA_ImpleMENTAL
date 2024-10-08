import time
import param # https://panel.holoviz.org/explanation/dependencies/param.html
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


AGE_WIDGET_INTERVALS = {
    "All": (1,150),
    "14-": (1,14), 
    "15-25": (15,25), 
    "26-40": (26,40), 
    "41-64": (41,64), 
    "65+": (65,150)
}


class age_widget(param.Parameterized):
    # By using param.Parameterized, the widget can be used as a parameter in other widgets
    # and its value can be watched
    value = param.List(default=[k for k in AGE_WIDGET_INTERVALS.keys()])

    def __init__(self, language_code: str):
        super().__init__()
        self._language_code = language_code
        # styles
        self.check_button_stylesheet = """
            :host(.solid) .bk-btn.bk-btn-default {
                background-color: white;
                color: #3e7d98;
                font-size: 8pt;
                font-weight: 600;
                padding: 4px 6px 4px 6px;
                transition: background-color 0.4s, color 0.4s;
            }
            :host(.solid) .bk-btn-group .bk-btn.bk-btn-default.bk-active {
                background-color: #3e7d98;
                color: white;
                box-shadow: none;
                transition: background-color 0.4s, color 0.4s;
            }
        """
        # widgets
        self.values = [k for k in AGE_WIDGET_INTERVALS.keys()]
        self.age_ranges = [k for k in AGE_WIDGET_INTERVALS.values()]
        self.age_ranges_to_tuple_dict = {k: v for k, v in AGE_WIDGET_INTERVALS.items()}
        self.panel_widget = panel.widgets.CheckButtonGroup(
            name=WIDGET_AGE_NAME_LANGDICT[self._language_code],
            value=[self.values[0]],
            options=self.values,
            stylesheets=[self.check_button_stylesheet]
        )
        # panel
        self._panel_styles = {
            "margin-left": "0px",
            "margin-right": "0px",
        }
        self._panel = panel.Column(
            self.panel_widget,
            styles=self._panel_styles
        )
        # widget value
        self.value = self.panel_widget.value
        self._panel_widget_selfwatcher = self.panel_widget.param.watch(self._update_age_intervals, "value")

    def _update_age_intervals(self, event):
        # first, unwatch the value to avoid infinite loops or many triggers
        self.panel_widget.param.unwatch(watcher=self._panel_widget_selfwatcher)
        # logic
        if self.values[0] in event.new and not (self.values[0] in event.old):
            # pressed the all button
            self.value = [self.values[0]]
            # if i update the value like this, the internal watcher will trigger
            self.panel_widget.value = [self.values[0]]
        elif self.values[0] in event.new and self.values[0] in self.panel_widget.value:
            # pressed the all button again, but it was already on all, so i turn off all and
            # turn on the other buttons
            self.value = [i for i in event.new if i != self.values[0]]
            self.panel_widget.value = [i for i in event.new if i != self.values[0]]
        elif sum([1 for i in event.new if i in self.values]) == len(self.values)-1:
            # all ages selected -> turn on all and off everything else
            self.value = [self.values[0]]
            self.panel_widget.value = [self.values[0]]
        elif len(event.new) != 0:
            self.value = event.new
        else:
            self.value = [self.values[0]]
            self.panel_widget.value = [self.values[0]]
        # ok done, reset the watcher
        self._panel_widget_selfwatcher = self.panel_widget.param.watch(self._update_age_intervals, "value")
    
    def update_language(self, language_code: str) -> None:
        if language_code not in WIDGET_AGE_ALL_AGES_TITLE.keys():
            raise ValueError("Language code not recognized:", language_code)
        self._language_code = language_code

    def get_panel(self, language_code: str) -> panel.Column:
        if language_code != self._language_code:
            self.update_language(language_code)
        return self._panel


class indicator_widget(param.Parameterized):
    # Here I have a widget containing multiple widgets.
    # Using param.Parameterized, I can watch the value of the whole widget
    # from the single widgets automatically.
    # An external watcher needs only to watch the value of the container widget
    # and not all values of the single widgets.
    # The widget container will have a "value" parameter which will contain the values
    # of all the single widgets.
    value = param.Dict(default={})

    def __init__(self, language_code: str):
        super().__init__()
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
                background-image: url('data:image/svg+xml;utf8,<svg version="1.1" viewBox="0 0 25 20" xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 25,0 12.5,20 Z" fill="#3e7d98ff" /></svg>')
            }
            option {
                background: #000000ff;
                background-color: #fbfbfbff;
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
        }
        self._panel_stylesheet = ""
        # widget container value
        self.value = {
            "age": self.widget_age_instance.value,
            "gender": self.widget_gender.value,
            "civil_status": self.widget_civil_status.value,
            "educational_level": self.widget_educational_level.value,
            "job_condition": self.widget_job_condition.value
        }
        self.widget_age_instance.param.watch(self._update_value, "value")
        self.widget_gender.param.watch(self._update_value, "value")
        self.widget_civil_status.param.watch(self._update_value, "value")
        self.widget_educational_level.param.watch(self._update_value, "value")
        self.widget_job_condition.param.watch(self._update_value, "value")

    def _update_value(self, event):
        # since value is a parameter, changing it in any way will trigger the watcher
        self.value = {
            "age": self.widget_age_instance.value,
            "age_default": [self.widget_age_instance.values[0]],
            "gender": self.widget_gender.value,
            "civil_status": self.widget_civil_status.value,
            "educational_level": self.widget_educational_level.value,
            "job_condition": self.widget_job_condition.value
        }
    
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
    # this test created the widget and uses fake data
    # to show widget - plot interactivity
    widgets_instance = indicator_widget(language_code="en")
    import bokeh.plotting
    import numpy
    plot = bokeh.plotting.figure()
    plot.title.text = "   "
    data_x = numpy.random.randint(3, 97, (1000))
    data_y = numpy.random.randn(1000)+5
    circ = plot.scatter(data_x, data_y, size=5, color="blue")

    def age_widget_2_plot_callback(event):
        # show only the selected age intervals in the plot (x axis)
        selected_intervals = event.new["age"]
        selected_intervals = [AGE_WIDGET_INTERVALS[i] for i in selected_intervals]
        selected_data_x = []
        selected_data_y = []
        for i in range(len(data_x)):
            for interval in selected_intervals:
                if interval[0] <= data_x[i] <= interval[1]:
                    selected_data_x.append(data_x[i])
                    selected_data_y.append(data_y[i])
                    break
        circ.data_source.data = {"x": selected_data_x, "y": selected_data_y}
        plot.title.text = f"Selected age intervals: {selected_intervals}"
        # color of the dots depending on gender
        color_dict = {
            "A": "blue",
            "A-U": "green",
            "M": "#0072b5",
            "F": "violet",
            "U": "black"
        }
        color = color_dict[event.new["gender"]]
        circ.glyph.fill_color = color
        circ.glyph.line_color = color

    widgets_instance.param.watch(age_widget_2_plot_callback, "value", precedence=100)
    
    app = panel.Row(
        widgets_instance.get_panel(language_code="en"),
        plot,
    )
    app.show()