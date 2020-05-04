import numpy as np
from bokeh import plotting
from bokeh.embed import components
from bokeh.io import curdoc
from bokeh.models import FuncTickFormatter, OpenURL, TapTool
from bokeh.models import Label, Legend, LegendItem, LogAxis, Range1d
from bokeh.themes import Theme

from utils import get_update_time, load_data, log_axis_labels

# get the exoplot theme
theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme

# what order to plot things and what the legend labels will say
missions = ['Kepler Candidate', 'Kepler Confirmed', 'K2 Candidate',
            'K2 Confirmed', 'TESS Candidate', 'Other Confirmed',
            'TESS Confirmed']

# markers and colors in the same order as the missions above
markers = ['circle_cross', 'circle', 'square_cross', 'square',
           'inverted_triangle', 'diamond', 'triangle']
# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas:
# https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#228833', '#ee6677', '#ee6677', '#ccbb44', '#aa3377',
          '#ccbb44']

# output files
embedfile = '_includes/period_radius_candidates_embed.html'
fullfile = '_includes/period_radius_candidates.html'

# set up the full output file
plotting.output_file(fullfile, title='Period Radius Plot')

# load the data
dfcon, dfkoi, dfk2, dftoi = load_data()

# what to display when hovering over a data point
TOOLTIPS = [
    ("Planet", "@planet"),
    # only give the decimal and sig figs if needed
    ("Period", "@period{0,0[.][0000]} days"),
    ("Radius", "@radius{0,0[.][00]} Earth; @jupradius{0,0[.][0000]} Jup"),
    ("Discovered by", "@discovery"),
    ("Status", "@status")
]

# create the figure
fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS,
                      plot_height=700)
# allow for something to happen when you click on data points
fig.add_tools(TapTool())

# need to store min and max radius values to create the second axis
ymin = 1
ymax = 1
# save the output plots to rearrange them in the legend
glyphs = []
counts = []

for ii, imiss in enumerate(missions):
    # candidates get these default values
    alpha = 0.35
    size = 4
    # select the appropriate set of planets for each mission
    # make the confirmed planets more opaque and bigger
    if imiss == 'Other Confirmed':
        good = ((~np.in1d(dfcon['pl_facility'], ['Kepler', 'K2', 'TESS'])) &
                np.isfinite(dfcon['pl_rade']) &
                np.isfinite(dfcon['pl_orbper']) &
                dfcon['pl_tranflag'].astype(bool))
        alpha = 0.7
        size = 8
    elif 'Confirmed' in imiss:
        fac = imiss.split()[0]
        good = ((dfcon['pl_facility'] == fac) & np.isfinite(dfcon['pl_rade']) &
                np.isfinite(dfcon['pl_orbper']) &
                dfcon['pl_tranflag'].astype(bool))
        alpha = 0.7
        size = 6
    elif 'Kepler' in imiss:
        good = ((dfkoi['koi_disposition'] == 'Candidate') &
                np.isfinite(dfkoi['koi_period']) &
                np.isfinite(dfkoi['koi_prad']))
        # what the hover tooltip draws its values from
        source = plotting.ColumnDataSource(data=dict(
                planet=dfkoi['kepoi_name'][good],
                period=dfkoi['koi_period'][good],
                radius=dfkoi['koi_prad'][good],
                jupradius=dfkoi['koi_pradj'][good],
                host=dfkoi['kepid'][good],
                discovery=dfkoi['pl_facility'][good],
                status=dfkoi['koi_disposition'][good],
                url=dfkoi['url'][good]
                ))
        print(imiss, ': ', good.sum())
    elif 'K2' in imiss:
        good = ((dfk2['k2c_disp'] == 'Candidate') &
                np.isfinite(dfk2['pl_rade']) &
                np.isfinite(dfk2['pl_orbper']) &
                dfk2['k2c_recentflag'].astype(bool))
        # what the hover tooltip draws its values from
        source = plotting.ColumnDataSource(data=dict(
                planet=dfk2['epic_candname'][good],
                period=dfk2['pl_orbper'][good],
                radius=dfk2['pl_rade'][good],
                jupradius=dfk2['pl_radj'][good],
                host=dfk2['epic_name'][good],
                discovery=dfk2['pl_facility'][good],
                status=dfk2['k2c_disp'][good],
                url=dfk2['url'][good]
                ))
        print(imiss, ': ', good.sum())
    else:
        good = ((dftoi['disp'] == 'Candidate') & np.isfinite(dftoi['prade']) &
                np.isfinite(dftoi['period']))
        # what the hover tooltip draws its values from
        source = plotting.ColumnDataSource(data=dict(
                planet=dftoi['TOI'][good],
                period=dftoi['period'][good],
                radius=dftoi['prade'][good],
                jupradius=dftoi['pradj'][good],
                host=dftoi['host'][good],
                discovery=dftoi['pl_facility'][good],
                status=dftoi['disp'][good],
                url=dftoi['url'][good]
                ))
        print(imiss, ': ', good.sum())
        alpha = 0.6
    counts.append(f'{good.sum():,}')

    if 'Confirmed' in imiss:
        # what the hover tooltip draws its values from
        source = plotting.ColumnDataSource(data=dict(
                planet=dfcon['pl_name'][good],
                period=dfcon['pl_orbper'][good],
                radius=dfcon['pl_rade'][good],
                jupradius=dfcon['pl_radj'][good],
                host=dfcon['pl_hostname'][good],
                discovery=dfcon['pl_facility'][good],
                status=dfcon['status'][good],
                url=dfcon['url'][good]
                ))
        print(imiss, ': ', good.sum())

    # plot the planets
    # nonselection stuff is needed to prevent planets in that category from
    # disappearing when you click on a data point ("select" it)
    glyph = fig.scatter('period', 'radius', color=colors[ii], source=source,
                        size=size, alpha=alpha, marker=markers[ii],
                        nonselection_alpha=alpha,
                        nonselection_color=colors[ii])
    glyphs.append(glyph)
    # save the global min/max
    ymin = min(ymin, source.data['radius'].min())
    ymax = max(ymax, source.data['radius'].max())

# set up where to send people when they click on a planet
url = "@url"
taptool = fig.select(TapTool)
taptool.callback = OpenURL(url=url)

# figure out what the default axis limits are
ydiff = np.log10(ymax) - np.log10(ymin)
ystart = 10.**(np.log10(ymin) - 0.05*ydiff)
yend = 10.**(np.log10(ymax) + 0.05*ydiff)

# jupiter/earth radius ratio
radratio = 11.21

# set up the second axis with the proper scaling
fig.extra_y_ranges = {"jup": Range1d(start=ystart/radratio, end=yend/radratio)}
fig.add_layout(LogAxis(y_range_name="jup"), 'right')

# add the first y-axis's label and use our custom log formatting for both axes
fig.yaxis.axis_label = 'Radius (Earth Radii)'
fig.yaxis.formatter = FuncTickFormatter(code=log_axis_labels())

# add the x-axis's label and use our custom log formatting
fig.xaxis.axis_label = 'Period (days)'
fig.xaxis.formatter = FuncTickFormatter(code=log_axis_labels())

# add the second y-axis's label
fig.right[0].axis_label = 'Radius (Jupiter Radii)'

# which order to place the legend labels
topleg = ['Kepler Confirmed', 'K2 Confirmed', 'TESS Confirmed']
bottomleg = ['Kepler Candidate', 'K2 Candidate', 'TESS Candidate']
vbottomleg = ['Other Confirmed']

# set up all the legend objects
items1 = [LegendItem(label=ii + f' ({counts[missions.index(ii)]})',
                     renderers=[glyphs[missions.index(ii)]])
          for ii in topleg]
items2 = [LegendItem(label=ii + f' ({counts[missions.index(ii)]})',
                     renderers=[glyphs[missions.index(ii)]])
          for ii in bottomleg]
items3 = [LegendItem(label=ii + f' ({counts[missions.index(ii)]})',
                     renderers=[glyphs[missions.index(ii)]])
          for ii in vbottomleg]

# create the two legends
for ii in np.arange(3):
    if ii == 0:
        items = items3
    elif ii == 1:
        items = items2
    else:
        items = items1
    legend = Legend(items=items, location="center")

    if ii == 2:
        legend.title = 'Discovered by and Status'
        legend.spacing = 10
    else:
        legend.spacing = 11

    legend.location = (-70, 5)
    legend.label_text_align = 'left'
    legend.margin = 0

    fig.add_layout(legend, 'above')

# overall figure title
fig.title.text = 'Transiting Planets and Planet Candidates'

# create the four lines of credit text in the two bottom corners
label_opts1 = dict(
    x=-85, y=42,
    x_units='screen', y_units='screen'
)

label_opts2 = dict(
    x=-85, y=47,
    x_units='screen', y_units='screen'
)

label_opts3 = dict(
    x=612, y=79,
    x_units='screen', y_units='screen', text_align='right',
    text_font_size='9pt'
)

label_opts4 = dict(
    x=612, y=83,
    x_units='screen', y_units='screen', text_align='right',
    text_font_size='9pt'
)

msg1 = 'By Exoplots'
# when did the data last get updated
modtimestr = get_update_time().strftime('%Y %b %d')
msg3 = 'Data: NASA Exoplanet Archive'
msg4 = 'and ExoFOP-TESS'

caption1 = Label(text=msg1, **label_opts1)
caption2 = Label(text=modtimestr, **label_opts2)
caption3 = Label(text=msg3, **label_opts3)
caption4 = Label(text=msg4, **label_opts4)

fig.add_layout(caption1, 'below')
fig.add_layout(caption2, 'below')
fig.add_layout(caption3, 'below')
fig.add_layout(caption4, 'below')

plotting.save(fig)

# save the individual pieces so we can just embed the figure without the whole
# html page
script, div = components(fig)
with open(embedfile, 'w') as ff:
    ff.write(div)
    ff.write(script)
