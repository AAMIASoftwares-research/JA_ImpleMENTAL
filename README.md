# JA_ImpleMENTAL
Code for the european Joint Action ImpleMENTAL, which tryes to raise awareness on mental health situation of countries and the need for proper data gathering and storing.


## RESOURCES

Here a list of resources used in the making of the dashboard

### Start Here: Reading SAS databases in python

Quick solution with pandas dataframes (which by the way integrate perfectly with the HoloViz tool):

```py
import pandas
df = pandas.read_sas("file_location.sas7bdat")
df.head()
```

Then, just convertit into numpy if necessary, and that's it!

- https://www.youtube.com/watch?v=coW7RUEw9PU
- https://www.marsja.se/how-to-read-sas-files-in-python-with-pandas/#google_vignette

### Start Here: DashBoard

Check out this video, in which description there are a lit of useful resources:
https://www.youtube.com/watch?v=tNAFtyjDPsI

Some help on plotting with different backends (bokeh, plotly, matplotlib):
https://hvplot.holoviz.org/user_guide/Plotting_Extensions.html

The subject is also touched here: https://holoviz.org/tutorial/Plotting.html

and specifically here: https://holoviz.org/tutorial/Plotting.html#save-and-further-customize-plots

## Useful packages for Dashboard Visualization and Serving in Python:

- The HoloViz ecosystem: https://holoviz.org/
