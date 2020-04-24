from bokeh import plotting
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import OpenURL, TapTool, FuncTickFormatter
import numpy as np
from bokeh.embed import components
from bokeh.models import LogAxis,  Range1d, Label, Legend, LegendItem
from utils import load_data, get_update_time, log_axis_labels
from datetime import datetime

# get the exoplot theme
theme = Theme(filename="./exoplots_theme.yaml")
# XXX: can't figure out why the theme value overrides anything we set below
# but only for this
theme._json['attrs']['Legend']['orientation'] = 'vertical'
curdoc().theme = theme

# what order to plot things and what the legend labels will say
methods = ['Other', 'Radial Velocity', 'Transit']

# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas:
# https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#ee6677', '#ccbb44', '#aa3377', '#4477aa',
          '#aaaaaa', '#66ccee']

colors = ['#ccbb44', '#ee6677', '#228833']

# output files
embedfile = '_includes/per_year_embed.html'
fullfile = '_includes/per_year.html'

# set up the full output file
plotting.output_file(fullfile, title='Planets Per Year')

# load the data
dfcon, dfkoi, dfk2, dftoi = load_data()

# create the figure
fig = plotting.figure(tooltips='@years $name: @$name') # y_axis_type='log'

years = range(dfcon['pl_disc'].min(), datetime.now().year+1)

data = {'years': years}
leglab = []

for ii, imeth in enumerate(methods):
    # select the appropriate set of planets for each mission
    if imeth == 'Other':
        good = ~np.in1d(dfcon['pl_discmethod'], methods)
    else:
        good = dfcon['pl_discmethod'] == imeth
        
    ll = []
    for iyear in years:
        ct = (dfcon['pl_disc'][good] == iyear).sum()
        #if ct == 0:
        #    ct = 0.1
        ll.append(ct)
    data[imeth] = ll
    leglab.append(imeth + f' ({good.sum():,})')
    
fig.vbar_stack(methods, x='years', width=0.9, color=colors, source=data,
               legend_label=leglab)

# add the first y-axis's label and use our custom log formatting for both axes
fig.yaxis.axis_label = 'Number'
#fig.yaxis.formatter = FuncTickFormatter(code=log_axis_labels())

# add the x-axis's label and use our custom log formatting
fig.xaxis.axis_label = 'Year of Confirmation'

# create the legend
legend = fig.legend
legend.location = 'top_left'
#legend.orientation = "vertical"
legend.title = 'Discovered via'
#legend.spacing = 10
#legend.margin = 8
 
# overall figure title
fig.title.text = 'Confirmed Planets'

# create the three lines of credit text in the two bottom corners
label_opts1 = dict(
    x=-84, y=42,
    x_units='screen', y_units='screen'
)

label_opts2 = dict(
    x=-84, y=47,
    x_units='screen', y_units='screen'
)

label_opts3 = dict(
    x=612, y=64,
    x_units='screen', y_units='screen', text_align='right',
    text_font_size='9pt'
)

msg1 = 'By Exoplots'
# when did the data last get updated
modtimestr = get_update_time().strftime('%Y %b %d')
msg3 = 'Data: NASA Exoplanet Archive'

caption1 = Label(text=msg1, **label_opts1)
caption2 = Label(text=modtimestr, **label_opts2)
caption3 = Label(text=msg3, **label_opts3)

fig.add_layout(caption1, 'below')
fig.add_layout(caption2, 'below')
fig.add_layout(caption3, 'below')

plotting.save(fig)

# save the individual pieces so we can just embed the figure without the whole
# html page
script, div = components(fig)
with open(embedfile, 'w') as ff:
    ff.write(div)
    ff.write(script)
