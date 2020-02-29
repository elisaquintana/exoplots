import pandas as pd
from bokeh import plotting
from bokeh import palettes
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import NumeralTickFormatter

theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme


datafile = 'data/confirmed-planets.csv'

df = pd.read_csv(datafile)

# get rid of the long name with just TESS
df['pl_facility'].replace('Transiting Exoplanet Survey Satellite (TESS)', 'TESS', inplace=True)


plotting.output_file('_includes/period_radius.html', title='Period Radius Plot')

TOOLTIPS = [
    ("Planet", "@planet"),
    ("Period", "@period{0,0[.]000}"),
    ("Radius", "@radius{0,0[.]00}"),
]

fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS)


missions = ['Kepler', 'K2', 'TESS']
colors = palettes.Category10[len(missions)]

for ii, imiss in enumerate(missions):
    good = df['pl_facility'] == imiss
    
    source = plotting.ColumnDataSource(data=dict(
    planet=df['pl_name'][good],
    period=df['pl_orbper'][good],
    radius=df['pl_rade'][good],
    ))
    
    
    fig.circle('period', 'radius', color=colors[ii], source=source, size=8,
               legend_label=imiss, muted_alpha=0.2, muted_color=colors[ii])


fig.yaxis.axis_label = 'Radius (Earth)'
fig.yaxis.formatter = NumeralTickFormatter(format='0,0[.]00')

fig.xaxis.axis_label = 'Period (days)'
fig.xaxis.formatter = NumeralTickFormatter(format='0,0[.]00')

fig.legend.location = 'bottom_right'
fig.legend.click_policy="hide"

fig.title.text = 'Confirmed Transiting Planets'



plotting.show(fig)

