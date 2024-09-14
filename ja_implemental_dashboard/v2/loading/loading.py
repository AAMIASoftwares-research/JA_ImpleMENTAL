import os
import panel
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

class Loading(object):
    def __init__(self):        
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
            z-index: -9999;
            background-color: #00000010;
            /*center the gif in the screen*/
            justify-content: center;
            align-items: center;
            display: flex;
            flex-direction: column;
        ">
            <img id="loading_gif" src="{self.gifs_urls_list[0]}" style="width: 100%; max-width: 7.0em; margin: 0; padding: 0;">
            <p style="color: #606060ff; font-size: 1.1em; margin: 0; padding: 0;">Loading...</p>
        </div>
        """+"""
        <script>
        function find_loading_element(){
            let element_id = "my_loading_html_element";
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
            // If it exists anywhere in the document, we return it. Otherwise, we return null.
            return null;
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
                const urls = """+str(self.gifs_urls_list)+""";
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
        </script>
        """
        return panel.pane.HTML(html, css_classes=['loading-div'], stylesheets=[self._panel_stylesheet])
    

if __name__ == "__main__":
    # TEST
    header = Loading()
    app = panel.Column(
        header.get_panel(),
        panel.Row(
            panel.pane.HTML(
                "<button onclick='loading_visible()'>Show Loading</button>",
            ),
            panel.pane.HTML(
                "<button onclick='loading_invisible()'>Hide Loading</button>",
            ),
        )
    )
    app.show()

