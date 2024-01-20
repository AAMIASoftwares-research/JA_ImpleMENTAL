import numpy as np

import pandas as pd
import hvplot.pandas

import holoviews             # uses bokeh as the default backend
holoviews.extension("bokeh") # Trivial to specify, but increases readability

import panel
panel.extension() # Define panel extension


# Generate random data
np.random.seed(0)
n = 100
data = pd.DataFrame({
    'x': np.random.rand(n),
    'y': np.random.rand(n),
    'height': np.random.rand(n)
})

# Create scatterplot (since we imported hvplot.pandas, we can use the hvplot method on the dataframe)
# - this object is a HoloViews Points object
scatterplot = data.hvplot.points(x='x', y='y', c='height', cmap='viridis', size=10, width=600, height=400)

# - however, to have more control over the plot, we can use the HoloViews API directly
# - - we can specify the dimensions (kdims) and values (vdims) of the plot in a rich way:
x_Dimension = holoviews.Dimension( 
    # https://holoviews.org/user_guide/Annotating_Data.html#dimension-parameters
    "x", # this will be x_Dimension.name
    label="$X$ dimension with a rich label",
    unit="m"
    # For the full list of parameters, you can call holoviews.help(holoviews.Dimension).
)
scatterplot = holoviews.Points(
        data, 
        kdims=[x_Dimension, 'y'], # for 'y' and 'height', the Dimension class is created automatically
        vdims=['height']
    ).opts(
        color='height',
        colorbar=True,
        size=10,
        width=600, 
        height=400,
        aspect="equal",
        nonselection_alpha=0.4,
        tools=['hover']
)

# Create dataframe table
table = panel.widgets.Tabulator(data, theme='site', pagination='remote', page_size=10)

# Create slider selector
height_range_slider = panel.widgets.RangeSlider(name='Height Range', start=0, end=1, value=(0, 1), step=0.05)

row_with_unbinded_elements = panel.Row(
    panel.Column(scatterplot, height_range_slider),
    table,
    styles={"background-color": "white"}
)

# LINKING WIDGETS (high level way with panel.bind)
# In this section we will learn how to link widgets to outputs “manually” rather than using .interactive.
# - this is useful when we want to have more control over the widgets and outputs
# - this is also useful when we want to link multiple widgets to the same output
# 
# Define callback function for slider which outputs a filtered dataframe dynamically
def filter_df(df, height_range):
    lower = df.height>height_range[0]
    upper = df.height<height_range[1]
    dffilter = lower & upper
    filtered_data = df[dffilter]
    return filtered_data

binded_table = panel.widgets.Tabulator(
    panel.bind(filter_df, df=data, height_range=height_range_slider),
    theme='site', pagination='remote', page_size=10
)

row_with_bindings = panel.Row(
    panel.Column(scatterplot, height_range_slider),
    binded_table,
    styles={"background-color": "lightblue"}
)


# LINKING WIDGETS (low level way with callbacks)
# In this section we will learn how to link widgets to outputs “manually” rather than using .interactive
# or panle.bind.
# For example, I cannot do holoviews.Points(panel.bind(....), ....) because the holoviews.Points class
# does not accept a callback as input.

# Panel also supports the more low-level approach of writing explicit callbacks that are 
# executed in response to changes in some parameter, e.g. the value of a widget. 
# All parameters can be watched using the 
#                                         .param.watch 
# API, which will call the provided callback with an event object containing
# the old and new value of the widget.

# Assigning a new value to the object of a pane will update the display.
# So, in this case, first we have to declare all panel objects, then we have to link them with callbacks.

scatterplot_panel = panel.panel(scatterplot) # automatically understands what backend to use
table_panel = panel.panel(table) # automatically understands what backend to use

# Define callback function for slider which outputs a filtered dataframe dynamically
def filter_df_callback(event):
    df = data
    height_range = event.new
    lower = df.height>height_range[0]
    upper = df.height<height_range[1]
    dffilter = lower & upper
    filtered_data = df[dffilter]
    # update scatterplot
    scatterplot_panel.object = holoviews.Points(
        filtered_data, 
        kdims=[x_Dimension, 'y'], # for 'y' and 'height', the Dimension class is created automatically
        vdims=['height']
    ).opts(
        # here, it is better to define an options dictionary and pass it to opts
        color='height',
        colorbar=True,
        size=10,
        width=600, 
        height=400,
        aspect="equal",
        nonselection_alpha=0.4,
        tools=['hover']
    )

height_range_slider.param.watch(filter_df_callback, 'value')

# now, the Tabulator widget is tricky because it does not have a .object attribute,
# and you cannot assign a new value to it.
# in this case, the Tabulator already provide the functionality for filtering based on a slider:
table_panel.add_filter(height_range_slider, 'height')
# else, you can resort to using panel.bind, but you have to define a function that returns the dataframe

row_with_callbacks = panel.Row(
    panel.Column(scatterplot_panel, height_range_slider),
    table_panel,
    styles={"background-color": "lightgreen"}
)


###############         OVERALL, PROBABLY BEST CHOICE IS TO USE PANEL.BIND






# Create panel application
# ------------------------
app = panel.Column(
    row_with_unbinded_elements,
    row_with_bindings,
    row_with_callbacks
)

# Show the application
app.show()
