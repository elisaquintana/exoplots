import pandas as pd
from bokeh import plotting
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import OpenURL, TapTool, FuncTickFormatter
import numpy as np
from bokeh.embed import components
from bokeh.models import LogAxis,  Range1d, Label, Legend, LegendItem
import os
from datetime import datetime

theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme

missions = ['Kepler Candidate', 'Kepler Confirmed', 'TESS Candidate', 
            'K2 Candidate', 'K2 Confirmed', 'Other Confirmed', 'TESS Confirmed']
# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas: https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#228833', '#ccbb44', '#ee6677', '#ee6677', '#aa3377', '#ccbb44']

#colors = ['#228833', '#ee6677', '#4477aa', '#aa3377', '#ccbb44',
#          '#aaaaaa', '#66ccee']
markers = ['circle_cross', 'circle', 'inverted_triangle', 'square_cross', 
           'square', 'diamond', 'triangle']


datafile = 'data/confirmed-planets.csv'
k2file = 'data/k2-candidates-table.csv'
koifile = 'data/kepler-kois-full.csv'


embedfile = '_includes/period_radius_candidates_embed.html'
fullfile = '_includes/period_radius_candidates.html'

dfcon = pd.read_csv(datafile)
dfk2 = pd.read_csv(k2file)
dfkoi = pd.read_csv(koifile)

modtimecon = datetime.fromtimestamp(os.path.getmtime(datafile))
modtimek2 = datetime.fromtimestamp(os.path.getmtime(k2file))
modtimekoi = datetime.fromtimestamp(os.path.getmtime(koifile))

# get rid of the long name with just TESS
dfcon['pl_facility'].replace('Transiting Exoplanet Survey Satellite (TESS)', 'TESS', inplace=True)
# set all of these planets as confirmed
dfcon['status'] = 'Confirmed'

# make these not all caps
dfkoi['koi_disposition'] = dfkoi['koi_disposition'].str.title()
dfk2['k2c_disp'] = dfk2['k2c_disp'].str.title()

# make KOIs into the format we expect
dfkoi['kepoi_name'].replace(to_replace='K0+', value='KOI-', regex=True, inplace=True)

# jupiter/earth radius ratio
radratio = 11.21
# give KOIs units of Jupiter radii
dfkoi['koi_pradj'] = dfkoi['koi_prad'] / radratio

# K2 tables don't have both columns always filled in
noearth = (~np.isfinite(dfk2['pl_rade']) & np.isfinite(dfk2['pl_radj']))
dfk2.loc[noearth, 'pl_rade'] = dfk2.loc[noearth, 'pl_radj'] * radratio

nojup = (np.isfinite(dfk2['pl_rade']) & (~np.isfinite(dfk2['pl_radj'])))
dfk2.loc[nojup, 'pl_radj'] = dfk2.loc[nojup, 'pl_rade'] / radratio


# run some checks to make sure things are as we think they should be
koicon = dfkoi['koi_disposition'] == 'Confirmed'
koican = dfkoi['koi_disposition'] == 'Candidate'
# XXX: keep working on this
notfound = ~np.in1d(dfkoi['kepler_name'][koicon], dfcon['pl_name'])

k2con = dfk2['k2c_disp'] == 'Confirmed'
k2can = dfk2['k2c_disp'] == 'Candidate'
notfound = ~np.in1d(dfk2['pl_name'][k2con], dfcon['pl_name'])

# set the appropriate discover facility for candidates
dfkoi['pl_facility'] = 'Kepler'
dfk2['pl_facility'] = 'K2'


# where do we want to point people to on clicking?
dfcon['url'] = 'https://exoplanetarchive.ipac.caltech.edu/overview/' + dfcon['pl_hostname']
dfk2['url'] = 'https://exofop.ipac.caltech.edu/k2/edit_target.php?id=' + dfk2['epic_name'].str.slice(5)
dfkoi['url'] = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/DisplayOverview/nph-DisplayOverview?objname=' + dfkoi['kepoi_name'].str.slice(0,-3) + '&type=KEPLER_TCE_HOST'

code = """
logtick = Math.log10(tick);
if ((logtick > -3) && (logtick < 3)){
    return tick.toLocaleString();
} else {
    power = Math.floor(logtick);
    retval = 10 + (power.toString()
             .split('')
             .map(function (d) { return d === '-' ? '⁻' : '⁰¹²³⁴⁵⁶⁷⁸⁹'[+d]; })
             .join(''));
    front = (tick/Math.pow(10, power)).toPrecision(2).toString().slice(0,3);
    
    if (front == '1.0'){
        return retval
    }
    else if (front.slice(1,3) == '.0'){
        return front[0] + 'x' + retval
    }
    
    return front + 'x' + retval
}
"""



plotting.output_file(fullfile, title='Period Radius Plot')

TOOLTIPS = [
    ("Planet", "@planet"),
    ("Period", "@period{0,0[.][0000]} days"),
    ("Radius", "@radius{0,0[.][00]} Earth; @jupradius{0,0[.][0000]} Jup"),
    ("Discovered by", "@discovery"),
    ("Status", "@status")
]

fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS) # y_range=(0.1,10)
fig.add_tools(TapTool())


ymin = 1
ymax = 1



glyphs = []
legs = []

for ii, imiss in enumerate(missions):  
    alpha = 0.3
    size = 4
    if imiss == 'Other Confirmed':
        good = ((~np.in1d(dfcon['pl_facility'], ['Kepler', 'K2', 'TESS'])) & np.isfinite(dfcon['pl_rade']) & 
                np.isfinite(dfcon['pl_orbper']) & dfcon['pl_tranflag'].astype(bool))
        alpha = 0.8
        size = 8
    elif 'Confirmed' in imiss:
        fac = imiss.split()[0]
        good = ((dfcon['pl_facility'] == fac) & np.isfinite(dfcon['pl_rade']) & 
                np.isfinite(dfcon['pl_orbper']) & dfcon['pl_tranflag'].astype(bool))
        alpha = 0.8
        size = 6
    elif 'Kepler' in imiss:
        good = ((dfkoi['koi_disposition'] == 'Candidate') & np.isfinite(dfkoi['koi_period']) & 
                np.isfinite(dfkoi['koi_prad']))
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
        good = ((dfk2['k2c_disp'] == 'Candidate') & np.isfinite(dfk2['pl_rade']) & 
                np.isfinite(dfk2['pl_orbper']) & dfk2['k2c_recentflag'].astype(bool))
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
        pass
            
    
    #alpha = 1. - good.sum()/1000.
    #alpha = max(0.2, alpha)
    
    if 'Confirmed' in imiss:
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
    
    glyph = fig.scatter('period', 'radius', color=colors[ii], source=source, size=size,
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

topleg = ['Kepler Confirmed', 'K2 Confirmed', 'TESS Confirmed', 'Other Confirmed']
bottomleg = ['Kepler Candidate', 'K2 Candidate', 'TESS Candidate']

items1 = [LegendItem(label=ii, renderers=[glyphs[missions.index(ii)]]) for ii in topleg]
items2 = [LegendItem(label=ii, renderers=[glyphs[missions.index(ii)]]) for ii in bottomleg]

for ii in np.arange(2):
    if ii == 0:
        items = items2
    else:
        items = items1
    legend = Legend(items=items, location="center")
    
    if ii == 1:
        legend.title = 'Discovered by and Status'
        legend.title_text_font_style = 'bold'
        legend.title_text_font_size = '14pt'
        legend.title_standoff = 0
        legend.spacing = 10
    else:
        legend.spacing = 11

    legend.location = (-60,5)
    legend.orientation = 'horizontal'
    legend.label_text_font_size = "14pt"
    legend.label_text_align = 'left'
    legend.margin = 0
    legend.border_line_color = None
    
    fig.add_layout(legend, 'above')
    legend.click_policy="hide"

fig.title.text = 'Transiting Planets and Planet Candidates'



modtimestr = modtimecon.strftime('%Y %b %d')

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

