import os
import panel
from .._panel_settings import PANEL_EXTENSION, PANEL_TEMPLATE, PANEL_SIZING_MODE
panel.extension(
    PANEL_EXTENSION,
    template=PANEL_TEMPLATE,
    sizing_mode=PANEL_SIZING_MODE
)


loading_gifs_urls = os.path.join(os.path.dirname(__file__), "..", "assets", "loading_gifs")


class Loading(object):
    def __init__(self):
        self._language_code = "en"
        self._loading_gifs_dir = loading_gifs_dir
        self.gif_file = [
            os.path.join(self._loading_gifs_dir, f) 
            for f in os.listdir(self._loading_gifs_dir) 
            if f.endswith(".gif")
        ][0]
        self._panel_stylesheet = """
            width: 100vw;
            margin: 0;
            padding: 0;
            background-color: #00ff3090;
        """
        
    def get_panel(self, **kwargs) -> panel.viewable.Viewable:
        html = f"""
        <div id="loading_html_element" style="width: 220px; margin: 0; padding: 0;">
            <img src="{self.gif_file}" style="width: 100%; margin: 0; padding: 0;">
        </div>
        """
        return panel.pane.HTML(html, stylesheets=[self._panel_stylesheet])
    

if __name__ == "__main__":
    # TEST
    header = Loading()
    header.get_panel().show()
        

