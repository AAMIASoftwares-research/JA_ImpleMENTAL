
# COORTE SELECTOR

def build_coorte_tooltip_html(value: str, text: str):
    s_ = """
        <p style="
            color: #888888ff;
            font-size: 0.9em;
            text-align: center;
        ">
    """
    s_ += "<span style='color:#707070ff;'><b>"+value+"</b></span></br>"
    e_ = "</p>"
    text = text.replace("\"", """<span style='color:#707070ff;'><b>""", 1)
    text = text.replace("\"", """</b></span>""", 1)
    return s_ + text + e_

def update_coorte_html(value):
    return panel.pane.HTML(build_coorte_tooltip_html(value, coorte_explain_dict[display_language][value]))

def build_body_coorte_selector():
    # buttons coorte selector
    coorte_button_options_list = [
        v for v in coorte_explain_dict[display_language].keys()
    ]
    global coorte_radio_group                                       ### THIS IS NOT A GOOD IDEA but i have to make it work
    style_sheet = """
    :host(.solid) .bk-btn.bk-btn-primary.bk-active {
        font-weight: bold;
        background-color: #005587ff;
    }
    """
    coorte_radio_group = panel.widgets.RadioButtonGroup(
        name='coorte selector', 
        options=coorte_button_options_list, 
        value=coorte_button_options_list[0],
        button_type='primary',
        stylesheets=[style_sheet]
    )
    # 
    coorte_selector_row = panel.Column(
        coorte_radio_group,
        panel.bind(update_coorte_html, coorte_radio_group.param.value)
    )
    return coorte_selector_row