import pandas as pd
from bokeh import plotting
from bokeh import palettes
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import NumeralTickFormatter

theme = Theme(filename="./ethan_theme.yaml")
curdoc().theme = theme


datafile = 'data/confirmed-planets.csv'

df = pd.read_csv(datafile)

# get rid of the long name with just TESS
df['pl_facility'].replace('Transiting Exoplanet Survey Satellite (TESS)', 'TESS', inplace=True)


plotting.output_file('_includes/period_radius.html', title='Period Radius Plot')

fig = plotting.figure(x_axis_type='log', y_axis_type='log')


missions = ['Kepler', 'K2', 'TESS']
colors = palettes.Category10[len(missions)]

for ii, imiss in enumerate(missions):
    good = df['pl_facility'] == imiss
    fig.circle(df['pl_orbper'][good], df['pl_rade'][good], color=colors[ii])


fig.yaxis.axis_label = 'Radius (Earth)'
fig.yaxis.axis_label_text_font_style = 'normal'
#fig.yaxis.axis_label_text_font_size = '24pt'
fig.yaxis.formatter = NumeralTickFormatter(format='0,0')

fig.xaxis.axis_label = 'Period (days)'
fig.xaxis.axis_label_text_font_style = 'normal'
#fig.xaxis.axis_label_text_font_size = '24pt'
fig.xaxis.formatter = NumeralTickFormatter(format='0,0')

fig.title.text = 'Confirmed Transiting Planets'

plotting.show(fig)

