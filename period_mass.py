import pandas as pd
from bokeh import plotting
from bokeh.themes import Theme
from bokeh.io import curdoc
from bokeh.models import NumeralTickFormatter, OpenURL, TapTool, FuncTickFormatter
import numpy as np
from bokeh.embed import components

theme = Theme(filename="./exoplots_theme.yaml")
curdoc().theme = theme

# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas: https://thenode.biologists.com/data-visualization-with-flying-colors/research/
colors = ['#228833', '#ee6677', '#66ccee', '#aa3377', '#ccbb44', '#4477aa', 
          '#aaaaaa']
markers = ['circle', 'square', 'triangle', 'diamond', 'inverted_triangle']


datafile = 'data/confirmed-planets.csv'

embedfile = '_includes/period_mass_embed.html'
fullfile = '_includes/period_mass.html'

df = pd.read_csv(datafile)

# get rid of the long name with just TESS
df['pl_facility'].replace('Transiting Exoplanet Survey Satellite (TESS)', 'TESS', inplace=True)


code = """
logtick = Math.log10(tick);
if ((logtick > -3) && (logtick < 4)){
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



plotting.output_file(fullfile, title='Period Mass Plot')

# XXX: switch from Jupiter to Earth masses at small planets. Also add an Earth mass axis
TOOLTIPS = [
    ("Planet", "@planet"),
    ("Period", "@period{0,0[.][0000]}"),
    ("Mass", "@mass{0,0[.][0000]}"),
    ("Discovered via", "@method")
]

fig = plotting.figure(x_axis_type='log', y_axis_type='log', tooltips=TOOLTIPS)
fig.add_tools(TapTool())


methods = ['Transit', 'Radial Velocity', 'Timing Variations', 'Other']

for ii, imeth in enumerate(methods):
    if imeth == 'Other':
        good = ((~np.in1d(df['pl_discmethod'], methods)) & (~df['pl_discmethod'].str.contains('Timing')) & 
                np.isfinite(df['pl_bmassj']) & np.isfinite(df['pl_orbper']))
        
    elif imeth == 'Timing Variations':
        good = (df['pl_discmethod'].str.contains('Timing') & 
                np.isfinite(df['pl_bmassj']) & np.isfinite(df['pl_orbper']))
    else:
        good = ((df['pl_discmethod'] == imeth) & np.isfinite(df['pl_bmassj']) & 
                np.isfinite(df['pl_orbper']))
    
    alpha = 1. - good.sum()/1000.
    alpha = max(0.2, alpha)
    
    source = plotting.ColumnDataSource(data=dict(
    planet=df['pl_name'][good],
    period=df['pl_orbper'][good],
    radius=df['pl_rade'][good],
    host=df['pl_hostname'][good],
    mass=df['pl_bmassj'][good],
    method=df['pl_discmethod'][good]
    ))
    print(good.sum())
    
    glyph = fig.scatter('period', 'mass', color=colors[ii], source=source, size=8,
               legend_label=imeth, muted_alpha=0.1, muted_color=colors[ii],
               alpha=alpha, marker=markers[ii], nonselection_alpha=alpha,
               nonselection_color=colors[ii])


url = "https://exoplanetarchive.ipac.caltech.edu/overview/@host"
taptool = fig.select(TapTool)
taptool.callback = OpenURL(url=url)


fig.yaxis.axis_label = 'Mass (Jupiter Masses)'
fig.yaxis.formatter = FuncTickFormatter(code=code)

fig.xaxis.axis_label = 'Period (days)'
#fig.xaxis.formatter = NumeralTickFormatter(format='0,0[.][00000]')
fig.xaxis.formatter = FuncTickFormatter(code=code)
# fig.xaxis.major_label_orientation = 'vertical'

# XXX: add "discovered via method" label to legend
fig.legend.location = 'bottom_right'
fig.legend.click_policy="hide"

fig.title.text = 'Confirmed Planets'

# XXX: need to add date/credit to this and every plot

plotting.save(fig)

script, div = components(fig)

with open(embedfile, 'w') as ff:
    ff.write(div)
    ff.write(script)

