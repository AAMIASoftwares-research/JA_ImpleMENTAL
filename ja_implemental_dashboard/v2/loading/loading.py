import os
import panel
import param
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)


loading_gifs_url_floder = "https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/"
gif_filenames = [
    f
    for f in os.listdir(
        os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "assets", "loading_gifs"
        )
    )
    if f.endswith(".gif")
]

def get_loading_gifs_urls_list() -> list[str]:
    return [
        loading_gifs_url_floder + f
        for f in gif_filenames
    ]

loading_js = """
<script type="text/javascript">
function findElementInWholeDocumentById(element_id){
    element = document.getElementById(element_id);
    if(element){
        return element;
    }
    // Depth-first search to find the loading element in the document.
    let root = document;
    while(root.host){
        root = root.host;
    }
    let stack = [root];
    while(stack.length > 0){
        let current = stack.pop();
        try{
            element_ = current.getElementById(element_id);
            if(element_){
                return element_;
            }
        }catch(e){
            // If the current element has no getElementById method, we just
            // add its children to the stack and continue.
        }
        let children = current.children;
        if(children){
            for(let i=0; i<children.length; i++){
                stack.push(children[i]);
            }
        }
        let shadow_roots = current.shadowRoot;
        if (shadow_roots){
            // if shadow_root is of type list:
            if (shadow_roots.length){
                for(let i=0; i<shadow_roots.length; i++){
                    stack.push(shadow_roots[i]);
                }
            }else{
                stack.push(shadow_roots);
            }
        }
    }
    return null;
}
function find_loading_element(){
    let element_id = "my_loading_html_element";
    return findElementInWholeDocumentById(element_id);
}
function find_loading_counter_element(){
    let element_id = "my_loading_counter_html_element";
    return findElementInWholeDocumentById(element_id);
}
function increase_loading_counter(){
    const counter_element = find_loading_counter_element();
    if (!counter_element){
        console.log('loading counter element not found');
        return;
    }
    let current_value = parseInt(counter_element.textContent);
    counter_element.textContent = current_value + 1;
}
function decrease_loading_counter(){
    const counter_element = find_loading_counter_element();
    if (!counter_element){
        console.log('loading counter element not found');
        return;
    }
    let current_value = parseInt(counter_element.textContent);
    current_value = current_value - 1;
    if (current_value < 0){ current_value = 0; }
    counter_element.textContent = current_value;
}
function loading_visible(){
    const div_element = find_loading_element();
    if (!div_element){
        console.log('loading element not found');
        return;
    }
    if(div_element.style.display != 'flex'){
        // set visible
        div_element.style.display = 'flex';
    }
}
function loading_invisible(){
    const div_element = find_loading_element();
    if (!div_element){
        console.log('loading element not found');
        return;
    }
    if(div_element.style.display != 'none'){
        // set invisible
        div_element.style.display = 'none';
        // change gif for next time
        const urls = """+f"{get_loading_gifs_urls_list()}"+""";
        const img_element = div_element.getElementsByTagName('img')[0];
        const current_index = urls.indexOf(img_element.src);
        random_index = Math.floor(Math.random() * urls.length);
        while(random_index == current_index){
            random_index = Math.floor(Math.random() * urls.length);
        }
        img_element.src = urls[random_index];
        // Chhange loading text
        let loading_text_options = [
            "Loading...",
            "Caricamento...",
            "Cargando...",
            "Chargement...",
            "Laden...",
            "Carregando...",
            
            "Please wait...",
            "Per favore, attendi...",
            "Por favor, espere...",
            "Bitte warten...",
            "Por favor, aguarde...",
            "Veuillez patienter...",

            "Just a moment...",
            "Un attimo...",
            "Un momento...",
            "Einen Moment...",
            "Um momento...",
            "Un instant...",

            "Almost there...",
            "Ci siamo quasi...",
            "Casi estamos...",
            "Presque là...",
            "Fast da...",
            "Quase lá...",

            "Hold on...",
            "Resisti...",
            "Aguanta...",
            "Halte durch...",
            "Aguente...",
            "Tiens bon...",

            "A little patience...",
            "Un attimo di pazienza...",
            "Un poco de paciencia...",
            "Ein wenig Geduld...",
            "Um pouco de paciência...",
            "Un peu de patience...",
        ];
        const p_element = div_element.getElementsByTagName('p')[0];
        p_element.textContent = loading_text_options[Math.floor(Math.random() * loading_text_options.length)];
    }
}
// Setupt job that every 0.3 seconds checks if the loading counter is greater than zero
// if it is, show the loading animation, if it is not, hide the loading animation.
setInterval(function(){
    const counter_element = find_loading_counter_element();
    if (!counter_element){
        console.log('loading counter element not found');
        return;
    }
    let current_value = parseInt(counter_element.textContent);
    if(current_value > 0){
        loading_visible();
    }else{
        loading_invisible();
    }
}, 300);
// Setup a job every 10 seconds to log the loading counter value
setInterval(function(){
    const counter_element = find_loading_counter_element();
    if (!counter_element){
        console.log('loading counter element not found');
        return;
    }
    console.log('loading counter value:', counter_element.textContent);
}, 10000);
// Setup a job every 5 minutes to reset the loading counter value
setInterval(function(){
    const counter_element = find_loading_counter_element();
    if (!counter_element){
        console.log('loading counter element not found');
        return;
    }
    counter_element.textContent = 0;
    console.log('loading counter value reset to 0 manually forcefully (in loading js)');
}, 5*60*1000);
</script>
"""

class Loading(object):
    def __init__(self):       
        self.do_nothing = False # set false to see loading animation
        self.gifs_urls_list = [
            loading_gifs_url_floder + f
            for f in gif_filenames
        ]
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
            z-index: 9998;
            background-color: #ffffff60;
            -webkit-backdrop-filter: blur(4px);
            -o-backdrop-filter: blur(4px);
            -moz-backdrop-filter: blur(4px);
            backdrop-filter: blur(4px);
            /*center the gif in the screen*/
            justify-content: center;
            align-items: center;
            display: flex;
            display: none; /* initially hidden */
            flex-direction: column;
        ">
            <img id="loading_gif" src="{self.gifs_urls_list[0]}" style="width: 100%; max-width: 7.0em; margin: 0; padding: 0;">
            <p style="color: #686868ff; font-size: 1.0em; font-weight: 600; margin: 0; padding: 0;">Loading...</p>
            <p id="my_loading_counter_html_element" style="display: none; color: #00000000;">0</p>
        </div>
        """ + loading_js
        if self.do_nothing:
            html = "<div style='display: none;'></div>"
        return panel.pane.HTML(html, css_classes=['loading-div'], stylesheets=[self._panel_stylesheet])
    
# Since communication between all components is messy,
# we will use a hidden text field that will contain a number greater equal to 0
# so that, when a component changes, it will increment this number, and when it finishes
# changing, it will decrement this number.
# if the number is greater than zero, the loading animation will be visible.
# if the number is equal to zero, the loading animation will be invisible.
# this through periodic checks every 0.3 seconds.

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
    widg_increase.value = not widg_increase.value

def decrease_loading_counter():
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

