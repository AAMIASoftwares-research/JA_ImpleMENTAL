import os, time, random
import panel
import param
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)

# This module uses javascript and cookies to keep track of a counter
# that will be increased or decreased by the elements when they change,
# so that the loading animation can be shown or hidden accordingly.
# Check out loading.js for more information.


with open(os.path.join(os.path.dirname(__file__), "loading.js"), "r") as f:
    _js = f.read()
loading_js = f"""
<script type="text/javascript">
{_js}
</script>
"""

class Loading(object):
    def __init__(self):       
        self.do_nothing = True # set false to see loading animation
        self._panel_stylesheet = """
            width: 100vw;
            margin: 0;
            padding: 0;
            background-color: #00ff3090;
        """
        
    def get_panel(self, **kwargs) -> panel.viewable.Viewable:
        html = f"""
        <div id="my_loading_html_element" style="
            /*make the div element take the whole screen*/
            margin: 0; 
            padding: 0;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9990;
            background-color: #ffffff30;
            -webkit-backdrop-filter: blur(1px);
            -o-backdrop-filter: blur(1px);
            -moz-backdrop-filter: blur(1px);
            backdrop-filter: blur(1px);
            /*center the gif in the screen*/
            justify-content: center;
            align-items: center;
            display: flex;
            display: none; /* initially hidden */
            flex-direction: column;
        ">
            <img id="loading_gif" src="" style="width: 100%; max-width: 7.0em; margin: 0; padding: 0;">
            <p style="color: #686868ff; font-size: 1.0em; font-weight: 600; margin: 0; padding: 0;">Loading...</p>
        </div>
        """ + loading_js
        if self.do_nothing:
            html = "<div style='display: none;'>No loading gifs.</div>"
        return panel.pane.HTML(html, css_classes=['loading-div'], stylesheets=[self._panel_stylesheet])
    
# Since communication between all components is messy,
# we will use a hidden text field that will contain a number greater equal to 0
# so that, when a component changes, it will increment this number, and when it finishes
# changing, it will decrement this number.
# if the number is greater than zero, the loading animation will be visible.
# if the number is equal to zero, the loading animation will be invisible.
# this through periodic checks every 0.3 seconds.
#
# The idea behind these two widgest it to import them into the dashboard
# and make them invisible, so that users cannot interact with them.
# One increases the counter, the other decreases it.
# You can import the two functions in any other module of the dashboard
# to increase or decrease the counter (usually, at the beginning and end of get_panel).
# You can import them as many times as you want, since each new instance
# will be connected to the same counter through the javascript functions.
widg_increase = panel.widgets.Toggle(name="Loading Counter Increase", value=False, visible=False)
widg_increase.jscallback(
    args={"widg": widg_increase},
    value="""
        increase_loading_counter();
    """
)
widg_decrease = panel.widgets.Toggle(name="Loading Counter Decrease", value=False, visible=False)
widg_decrease.jscallback(
    args={"widg": widg_decrease},
    value="""
        decrease_loading_counter(); 
    """
)
def increase_loading_counter():
    time.sleep(random.random()*0.4)
    widg_increase.value = not widg_increase.value

def decrease_loading_counter():
    time.sleep(random.random()*0.4)
    widg_decrease.value = not widg_decrease.value

if __name__ == "__main__":
    # TEST    
    def get_html(text):
        # This pipeline, in this case, is completely general
        # first thing, tell the dashboard you are starting to change something
        increase_loading_counter()
        # do your stuff here
        import time
        time.sleep(4)
        # last thing, tell the dashboard you are finished changing something
        decrease_loading_counter()
        # return
        return panel.pane.HTML(f"<h1>Test: {text}</h1>")
    widget=panel.widgets.RadioButtonGroup(
        options=["Left", "Right"],
        value="Left",
        name="Do nothing",
    )
    header = Loading()
    app = panel.Column(
        #global_loading_js_pane,
        header.get_panel(),
        panel.Row(
            panel.pane.HTML(
                "<button onclick='loading_visible()'>Show Loading</button>",
            ),
            panel.pane.HTML(
                "<button onclick='loading_invisible()'>Hide Loading</button>",
            ),
        ),
        panel.bind(get_html, widget),
        widget,
        widg_increase,
        widg_decrease,
    )
    app.show()

