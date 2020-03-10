from bokeh import plotting
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import OpenURL, TapTool, FuncTickFormatter
import numpy as np
from bokeh.embed import components
from bokeh.models import LogAxis,  Range1d, Label, Legend, LegendItem
from utils import load_data, get_update_time, log_axis_labels

theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme

# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas: https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#ee6677', '#4477aa', '#aa3377', '#ccbb44',
          '#aaaaaa', '#66ccee']
markers = ['circle', 'square', 'triangle', 'diamond', 'inverted_triangle']


embedfile = '_includes/period_radius_embed.html'
fullfile = '_includes/period_radius.html'



dfcon, dfkoi, dfk2, dftoi = load_data()


code = log_axis_labels(max_tick=5)



plotting.output_file(fullfile, title='Period Radius Plot')

TOOLTIPS = [
    ("Planet", "@planet"),
    ("Period", "@period{0,0[.][0000]} days"),
    ("Radius", "@radius{0,0[.][00]} Earth; @jupradius{0,0[.][0000]} Jup"),
    ("Discovered by", "@discovery")
]

fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS) # y_range=(0.1,10)
fig.add_tools(TapTool())


ymin = 1
ymax = 1


missions = ['Kepler', 'K2', 'TESS', 'Other']



glyphs = []
legs = []

for ii, imiss in enumerate(missions):    
    if imiss == 'Other':
        good = ((~np.in1d(dfcon['pl_facility'], missions)) & np.isfinite(dfcon['pl_rade']) & 
                np.isfinite(dfcon['pl_orbper']) & dfcon['pl_tranflag'].astype(bool))
    else:
        good = ((dfcon['pl_facility'] == imiss) & np.isfinite(dfcon['pl_rade']) & 
                np.isfinite(dfcon['pl_orbper']) & dfcon['pl_tranflag'].astype(bool))
    
    alpha = 1. - good.sum()/1000.
    alpha = max(0.2, alpha)
    
    source = plotting.ColumnDataSource(data=dict(
    planet=dfcon['pl_name'][good],
    period=dfcon['pl_orbper'][good],
    radius=dfcon['pl_rade'][good],
    jupradius=dfcon['pl_radj'][good],
    host=dfcon['pl_hostname'][good],
    discovery=dfcon['pl_facility'][good],
    url=dfcon['url'][good]
    ))
    print(imiss, ': ', good.sum())
    
    glyph = fig.scatter('period', 'radius', color=colors[ii], source=source, size=8,
               muted_alpha=0.1, muted_color=colors[ii],
               alpha=alpha, marker=markers[ii], nonselection_alpha=alpha,
               nonselection_color=colors[ii])
    glyphs.append(glyph)
    legs.append(imiss)
    
    ymin = min(ymin, source.data['radius'].min())
    ymax = max(ymax, source.data['radius'].max())

url = "@url"
taptool = fig.select(TapTool)
taptool.callback = OpenURL(url=url)



ydiff = np.log10(ymax) - np.log10(ymin)

ystart = 10.**(np.log10(ymin) - 0.05*ydiff)
yend = 10.**(np.log10(ymax) + 0.05*ydiff)

# jupiter/earth radius ratio
radratio = 11.21

fig.extra_y_ranges = {"jup": Range1d(start=ystart/radratio, end=yend/radratio)}
fig.add_layout(LogAxis(y_range_name="jup"), 'right')



fig.yaxis.axis_label = 'Radius (Earth Radii)'
fig.yaxis.formatter = FuncTickFormatter(code=code)

fig.xaxis.axis_label = 'Period (days)'
#fig.xaxis.formatter = NumeralTickFormatter(format='0,0[.][00000]')
fig.xaxis.formatter = FuncTickFormatter(code=code)
# fig.xaxis.major_label_orientation = 'vertical'

fig.right[0].axis_label = 'Radius (Jupiter Radii)'
# fig.right[0].major_label_orientation = 5.

items = [LegendItem(label=ii, renderers=[jj]) for ii, jj in zip(legs, glyphs)]
legend = Legend(items=items, location="center")
legend.title = 'Discovered by'
legend.orientation = 'horizontal'
legend.label_text_font_size = "14pt"

legend.title_text_font_style = 'bold'
legend.title_text_font_size = '14pt'
legend.title_standoff = 0
legend.margin = 3
legend.border_line_color = None
legend.spacing = 25

fig.add_layout(legend, 'above')
legend.click_policy="hide"

fig.title.text = 'Confirmed Transiting Planets'



modtimestr = get_update_time().strftime('%Y %b %d')

label_opts1 = dict(
    x=-68, y=42,
    x_units='screen', y_units='screen'
)

label_opts2 = dict(
    x=-68, y=47,
    x_units='screen', y_units='screen'
)

label_opts3 = dict(
    x=627, y=64,
    x_units='screen', y_units='screen', text_align='right',
    text_font_size='9pt'
)

msg1 = 'By Exoplots'
msg3 = 'Data: NASA Exoplanet Archive'

caption1 = Label(text=msg1, **label_opts1)
caption2 = Label(text=modtimestr, **label_opts2)
caption3 = Label(text=msg3, **label_opts3)

fig.add_layout(caption1, 'below')
fig.add_layout(caption2, 'below')
fig.add_layout(caption3, 'below')

plotting.save(fig)

script, div = components(fig)

with open(embedfile, 'w') as ff:
    ff.write(div)
    ff.write(script)

