import bokeh
import panel
panel.extension()

if __name__ == "__main__":
    # Create a Panel layout
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]
    bokeh_scatter = bokeh.plotting.figure(title="A Bokeh plot", max_width=300)
    bokeh_scatter.scatter(x=x, y=y, size=10, color="navy", alpha=1.0)
    app = panel.Column(
        panel.pane.Markdown("## A Panel app"),
        panel.pane.Bokeh(bokeh_scatter),
    )
    app.show()
