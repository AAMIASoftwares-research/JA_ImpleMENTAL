const loading_gifs_url_floder = "https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/";

const loading_gifs_urls = [
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/04de2e31234507.564a1d23645bf.gif',
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/09b24e31234507.564a1d23c07b4.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/35771931234507.564a1d2403b3a.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/3f3a3831234507.564a1d2338123.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/585d0331234507.564a1d239ac5e.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/ab79a231234507.564a1d23814ef.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/c3c4d331234507.564a1d23db8f9.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/cd514331234507.564a1d2324e4e.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/dae67631234507.564a1d230a290.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/f1055231234507.564a1d234bfb6.gif', 
    'https://raw.githubusercontent.com/AAMIASoftwares-research/JA_ImpleMENTAL/main/assets/loading_gifs/loading_lightbulb.gif'
];
const loading_text_options = [
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

var g_loading_counter = 0;

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

function increase_loading_counter(){
    g_loading_counter = g_loading_counter + 1;
    return;
}

function decrease_loading_counter(){
    g_loading_counter = g_loading_counter - 1;
    return;
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
        // Check if image has a source
        const img_element = div_element.getElementsByTagName('img')[0];
        if(!img_element.src || img_element.src == '' || !loading_gifs_urls.includes(img_element.src)){
            // Set a random source
            random_index = Math.floor(Math.random() * loading_gifs_urls.length);
            img_element.src = loading_gifs_urls[random_index];
        }
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
        const img_element = div_element.getElementsByTagName('img')[0];
        const current_index = loading_gifs_urls.indexOf(img_element.src);
        random_index = Math.floor(Math.random() * loading_gifs_urls.length);
        while(random_index == current_index){
            random_index = Math.floor(Math.random() * loading_gifs_urls.length);
        }
        img_element.src = loading_gifs_urls[random_index];
        // Change loading text using random text from loading_text_options
        const p_element = div_element.getElementsByTagName('p')[0];
        p_element.textContent = loading_text_options[Math.floor(Math.random() * loading_text_options.length)];
    }
}

// Setupt job that every 0.3 seconds checks if the loading counter is greater than zero
// if it is, show the loading animation, if it is not, hide the loading animation.
function job_show_hide_loading(){
    // with global variable
    if (g_loading_counter > 0){
        loading_visible();
    }
    else{
        loading_invisible();
    }
    return;
}
setInterval(
    job_show_hide_loading,
    500
);

// Set up a job to change the loading text every 15 seconds
setInterval(
    function(){
        const div_element = find_loading_element();
        if (!div_element){
            console.log('loading element not found');
            return;
        }
        if(div_element.style.display != 'none'){
            // Chhange loading text
            const p_element = div_element.getElementsByTagName('p')[0];
            p_element.textContent = loading_text_options[Math.floor(Math.random() * loading_text_options.length)];
        }
    }, 
    15000
);


