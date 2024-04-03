from panel.theme import Material

def build_indicator_type_tabs():
    tab_evaluation = build_evaluation_indicators_tab() # evaluation is created before monitoring because it needs the coorte selector, otherwise the build_body_main_box() cannot access coorte_selector_value=coorte_radio_group.param.value . This is poor design but it is just a quick fix for the UI.
    tab_monitoring = build_monitoring_indicators_tab()
    style_sheet = """
        :host(.bk-above) {
            # to modify all the tab ememnts (or, the elemnt inside the tab div)
        }
        :host(.bk-above) .bk-header{
            # to modify the header of the tab
        }
        :host(.bk-above) .bk-header .bk-tab {
            border-bottom-width: 4px;
            color: #909090ff;
            border-bottom-color: #909090ff;
        }
        :host(.bk-above) .bk-header .bk-tab.bk-active {
            background: #0072b5ff;
            color: #fafafaff;
            font-weight: bold;
            border-bottom-color: #025383ff;
        }
    """
    # https://panel.holoviz.org/how_to/styling/apply_css.html
    tabs = panel.Tabs(
        (monitoring_indicators_langmap[display_language], tab_monitoring),
        (evaluation_indicators_langmap[display_language], tab_evaluation),
        tabs_location="above",
        active=0,
        styles={
            "margin-top": "0px",
            "padding-top": "0px",
            "margin-bottom": "35px",
            "--pn-tab-active-color": "#ff1155ff"
        },
        design=Material,
        stylesheets=[style_sheet]
    )
    return tabs

