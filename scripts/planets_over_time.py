from datetime import datetime, timedelta

import numpy as np
from bokeh import plotting
from bokeh.embed import components
from bokeh.io import curdoc
from bokeh.models import Label
from bokeh.themes import Theme
from bokeh.models import FuncTickFormatter, NumeralTickFormatter
from bokeh.models.tools import HoverTool

from utils import get_update_time, load_data, log_axis_labels

# get the exoplot theme
theme = Theme(filename="./exoplots_theme.yaml")
# XXX: can't figure out why the theme value overrides anything we set below
#   but only for this
theme._json['attrs']['Legend']['orientation'] = 'vertical'
curdoc().theme = theme

# what order to plot things and what the legend labels will say
methods = ['Other', 'Radial Velocity', 'Transit']

# colorblind friendly palette from https://personal.sron.nl/~pault/
# other ideas:
# https://thenode.biologists.com/data-visualization-with-flying-colors/research/
# colors = ['#228833', '#ee6677', '#ccbb44', '#aa3377', '#4477aa',
#           '#aaaaaa', '#66ccee']

colors = ['#ccbb44', '#ee6677', '#228833']

# output files
embedfile = '_includes/per_year_embed.html'
fullfile = '_includes/per_year.html'

embedfilelog = '_includes/per_year_log_embed.html'
fullfilelog = '_includes/per_year_log.html'

embedfilecum = '_includes/per_year_cumul_embed.html'
fullfilecum = '_includes/per_year_cumul.html'

embedfilecumlog = '_includes/per_year_cumul_log_embed.html'
fullfilecumlog = '_includes/per_year_cumul_log.html'

# load the data
dfcon, dfkoi, dfk2, dftoi = load_data()

years = range(dfcon['pl_disc'].min(), datetime.now().year+1)

data = {'years': years}
cumul = {'years': years}
leglab = []
tots = []
cumtots = []

for ii, imeth in enumerate(methods):
    # select the appropriate set of planets for each mission
    if imeth == 'Other':
        good = ~np.in1d(dfcon['pl_discmethod'], methods)
    else:
        good = dfcon['pl_discmethod'] == imeth

    ll = []
    base = []
    isum = [0]
    for iyear in years:
        ct = (dfcon['pl_disc'][good] == iyear).sum()
        # if ct == 0:
        #    ct = 0.1
        ll.append(ct)
        isum.append(isum[-1] + ct)
        base.append(0.01)
    isum.pop(0)
    
    cumtots.append(isum)
    tots.append(ll)
    data[imeth] = ll
    cumul[imeth] = isum
    if ii == 0:
        data['base'] = base
        cumul['base'] = base
    leglab.append(imeth + f' ({good.sum():,})')


tots = np.array(tots).sum(axis=0)
cumtots = np.array(cumtots).sum(axis=0)

data['total'] = tots
cumul['total'] = cumtots

# get the exponential growth bit
cyear = get_update_time().year
fullyear = datetime(cyear + 1, 1, 1) - datetime(cyear, 1, 1)
# extrapolate this year's total through the full year
upscale = fullyear / (get_update_time() - datetime(cyear, 1, 1))
scaled = cumtots * 1
scaled[-1] = scaled[-2] + upscale * (scaled[-1] - scaled[-2])
# use a weighted exponential growth fit
# see https://mathworld.wolfram.com/LeastSquaresFittingExponential.html
exp = np.polyfit(np.arange(scaled.size), np.log(scaled), 1, w=np.log(scaled))

preds = np.exp(np.polyval(exp, np.arange(scaled.size)))

tdouble = np.log(2) / exp[0]

cumul['Predicted'] = preds


# make the per year and then cumulative plots
for xx in np.arange(2):
    if xx == 0:
        fancytool = """
            <div>
                <span style="font-size: 12px; float:right;">@$name{0,0}</span>
                <span style="font-size: 12px; color: #5caddd; float:right;">@years $name:</span>          
            </div>
            <div>
                <span style="font-size: 12px; float:right;">@total{0,0}</span>
                <span style="font-size: 12px; color: #5caddd; float:right;">@years Total:</span> 
            </div>"""
    else:
        fancytool = """
            <div>
                <span style="font-size: 12px; float:right;">@$name{0,0}</span>
                <span style="font-size: 12px; color: #5caddd; float:right;">Through @years $name:</span>          
            </div>
            <div>
                <span style="font-size: 12px; float:right;">@total{0,0}</span>
                <span style="font-size: 12px; color: #5caddd; float:right;">Through @years Total:</span> 
            </div>"""
    # set up the full output file and create the figure
    if xx == 0:
        plotting.output_file(fullfile, title='Planets Per Year')
        # '@years $name: @$name; Total: @total'
        fig = plotting.figure(tooltips=fancytool,
                          y_range=(0, tots.max()*1.05))
        fig.vbar_stack(methods, x='years', width=0.9, color=colors, source=data,
                   legend_label=leglab, line_width=0)
    else:
        plotting.output_file(fullfilecum, title='Cumulative Planets')
        fig = plotting.figure(tooltips=fancytool,
                          y_range=(0, cumtots.max()*1.05))
        # plot the exponential growth
        fig.line('years', 'Predicted', source=cumul, line_width=5, line_color='black',
                 legend_label=f'Doubling Time: {tdouble:.2f} years', name='Predicted')
        fig.vbar_stack(methods, x='years', width=0.9, color=colors, source=cumul,
                   legend_label=leglab, line_width=0)

    # add the first y-axis's label and use our custom log formatting for both axes
    fig.yaxis.axis_label = 'Number'
    fig.yaxis.formatter = NumeralTickFormatter(format='0,0')
    
    # add the x-axis's label and use our custom log formatting
    fig.xaxis.axis_label = 'Year of Confirmation'
    
    # create the legend
    legend = fig.legend
    legend.location = 'top_left'
    # legend.orientation = "vertical"
    legend.title = 'Discovered via'
    # legend.spacing = 10
    # legend.margin = 8
    legend[0].items = legend[0].items[::-1]
        
    # overall figure title
    if xx == 0:
        fig.title.text = f'Confirmed Planets Per Year ({cumtots[-1]:,})'
    else:
        fig.title.text = f'Cumulative Confirmed Planets ({cumtots[-1]:,})'
    
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
    if xx == 0:
        with open(embedfile, 'w') as ff:
            ff.write(div)
            ff.write(script)
    else:
        with open(embedfilecum, 'w') as ff:
            ff.write(div)
            ff.write(script)
    
    
    
# now do the same thing but on log scale

methods.insert(0,'base')
colors.insert(0, '#000000')
leglab.insert(0,'')

# make the per year and then cumulative plots
for xx in np.arange(2):
    ymin = 0.8
    # set up the full output file and create the figure
    if xx == 0:
        ymax = 10.**(np.log10(tots.max()) + 0.05*(np.log10(tots.max()) - np.log10(ymin)))
        plotting.output_file(fullfilelog, title='Planets Per Year Log')
        fig2 = plotting.figure(tooltips=fancytool,
                          y_range=(ymin, ymax), y_axis_type='log')
        fig2.vbar_stack(methods, x='years', width=0.9, color=colors, source=data,
                    legend_label=leglab, line_width=0)
    else:
        ymax = 10.**(np.log10(cumtots.max()) + 0.065*(np.log10(cumtots.max()) - np.log10(ymin)))
        plotting.output_file(fullfilecumlog, title='Planets Per Year Log')
        fig2 = plotting.figure(tooltips=fancytool,
                          y_range=(ymin, ymax), y_axis_type='log')
        # plot the exponential growth
        fig2.line('years', 'Predicted', source=cumul, line_width=5, line_color='black',
                  legend_label=f'Doubling Time: {tdouble:.2f} years', name='Predicted')
        fig2.vbar_stack(methods, x='years', width=0.9, color=colors, source=cumul,
                    legend_label=leglab, line_width=0)
    
    # add the first y-axis's label and use our custom log formatting for both axes
    fig2.yaxis.axis_label = 'Number'
    fig2.yaxis.formatter = FuncTickFormatter(code=log_axis_labels(max_tick=4))
    
    # add the x-axis's label and use our custom log formatting
    fig2.xaxis.axis_label = 'Year of Confirmation'
    
    # create the legend 
    legend = fig2.legend
    legend.location = 'top_left'
    # legend.orientation = "vertical"
    legend.title = 'Discovered via'
    # legend.spacing = 10
    # legend.margin = 8
    
    # overall figure title
    if xx == 0:
        fig2.title.text = f'Confirmed Planets Per Year ({cumtots[-1]:,})'
    else:
        fig2.title.text = f'Cumulative Confirmed Planets ({cumtots[-1]:,})'

    legend[0].items.pop(1)
    legend[0].items = legend[0].items[::-1]
    
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
    
    fig2.add_layout(caption1, 'below')
    fig2.add_layout(caption2, 'below')
    fig2.add_layout(caption3, 'below')
    
    plotting.save(fig2)
    
    # save the individual pieces so we can just embed the figure without the whole
    # html page
    script, div = components(fig2)
    if xx == 0:
        with open(embedfilelog, 'w') as ff:
            ff.write(div)
            ff.write(script)
    else:
        with open(embedfilecumlog, 'w') as ff:
            ff.write(div)
            ff.write(script)    






cyear = get_update_time().year
fullyear = datetime(cyear + 1, 1, 1) - datetime(cyear, 1, 1)
upscale = fullyear / (get_update_time() - datetime(cyear, 1, 1))

scaled = cumtots * 1
scaled[-1] = scaled[-2] + upscale * (scaled[-1] - scaled[-2])


import matplotlib.pyplot as plt


plt.close('all')
exp1 = np.polyfit(np.arange(scaled.size), np.log(scaled), 1)
exp2 = np.polyfit(np.arange(scaled.size), np.log(scaled), 1, w=scaled)
exp3 = np.polyfit(np.arange(scaled.size), np.log(scaled), 1, w=np.log(scaled))



plt.figure()
plt.scatter(np.arange(scaled.size), scaled)

plt.plot(np.exp(np.polyval(exp1, np.arange(scaled.size))), label='x1')
plt.plot(np.exp(np.polyval(exp2, np.arange(scaled.size))), label='x2')
plt.plot(np.exp(np.polyval(exp3, np.arange(scaled.size))), label='x3')

plt.legend()



plt.figure()
plt.scatter(np.arange(scaled.size), np.log(scaled))

plt.plot(np.polyval(exp1, np.arange(scaled.size)), label='x1')
plt.plot(np.polyval(exp2, np.arange(scaled.size)), label='x2')
plt.plot(np.polyval(exp3, np.arange(scaled.size)), label='x3')

plt.legend()












