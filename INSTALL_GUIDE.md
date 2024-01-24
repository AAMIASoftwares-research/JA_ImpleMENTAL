# Guide to install and use the JA ImpleMENTAL dashboards

## Dashboard v0 - 2024-01-24

Dashboard v0 is situated in the subfolder ```./ja_implemental_dashboard/v0/``` and contains only the file ```dashboard.py```, which is a standalone python file containing a program to run the dashboard.

### How to install

This dashboard uses python to run. Be sure to have python installed on your system. I recomend [this version of python (3.11)](https://www.python.org/downloads/release/python-3117/). Open the installer and install python. Be sure to install it on the side with other python versions, for all users, and add it to PATH. The path python will be installed to should look something like ```C:\Program Files\PYTHON311``` or similar (it is a short path, if you see a long path, select to install python for all users and the isntallation path should change automatically). 

Then, open a terminal and navigate to the folder this installation guide file is situated in (go to this folder, right click anywhere, "open in Terminal" or similar).

Run the following command, that will create a virtual environment to install all the needed requirements, so that when you do don't need this project anymore, you can just delete the folder and everything will be gone:

```python -m venv venv```

Then, run the following commands to activate the virtual environment and install the requirements:

```.\venv\Scripts\activate```

```python -m pip install --upgrade pip```

```python -m pip install numpy pandas matplotlib plotly bokeh```

```python -m pip install holoviews[recommended]```

```python -m pip install hvplot holoviews[recommended] geoviews datashader panel```

Good, now you should be able to run the dashboard. To do so, run the following command from the terminal (same location as this guide, should be ...\\...\\JA_ImpleMENTAL>):

```python -m ja_implemental_dashboard.v0.dashboard```

This should automatically open your preferred web browser after a few seconds, and opens the page. Be sure to have internet connection! This was developed in Google Chrome, so try using that browser if you have any problems (set it as the default one and then try again).

