"""
Utility functions needed for nearly every figure. Better to put things here
once and then only change it once if a change is needed rather than 
copy/paste the same things for a new figure idea and have to track it down in 
every file it was used to change it.
"""


def get_update_time():
    """
    Return a datetime object representing the last time all the data files 
    were generated.

    Returns
    -------
    datetime.datetime

    """
    import datetime
    dateloc = 'data/last_update_time.txt'
    with open(dateloc, 'r') as ff:
        lines = ff.readlines()
    return datetime.datetime.strptime(lines[0], '%Y-%m-%d %H:%M:%S.%f')


def load_data():
    """
    Load our data tables and perform some data cleansing/updating to make them
    ready for use in our interactive figures.

    Returns
    -------
    dfcon : DataFrame
        All planets in the Exoplanet Archive confirmed planets table.
    dfkoi : DataFrame
        All planets in the Exoplanet Archive KOI planets table.
    dfk2 : DataFrame
        All planets in the Exoplanet Archive K2 planet candidates table.
    dftoi : DataFrame
        All planets in the ExoFOP-TESS planet candidates table.

    """
    import pandas as pd
    import numpy as np
    # load the data files
    datafile = 'data/confirmed-planets.csv'
    k2file = 'data/k2-candidates-table.csv'
    koifile = 'data/kepler-kois-full.csv'
    toifile = 'data/tess-candidates.csv'
    
    dfcon = pd.read_csv(datafile)
    dfk2 = pd.read_csv(k2file)
    dfkoi = pd.read_csv(koifile)
    dftoi = pd.read_csv(toifile)
    
    # replace the long name with just TESS
    full = 'Transiting Exoplanet Survey Satellite (TESS)'
    dfcon['pl_facility'].replace(full, 'TESS', inplace=True)
    # set all of these planets as confirmed
    dfcon['status'] = 'Confirmed'
    
    # get easier to reference names for things in the ExoFOP listing
    renames = {'TFOPWG Disposition': 'disp', 'TIC ID': 'TIC',
               'Period (days)': 'period',
               'Planet Radius (R_Earth)': 'prade'}
    dftoi.rename(columns=renames, inplace=True)
    
    # things that don't have a disposition get PC
    dftoi['disp'].replace(np.nan, 'PC', inplace=True)
    # change this to the status we want to report
    dftoi['disp'].replace('PC', 'Candidate', inplace=True)
    
    # set these to strings we'd want to show in a figure
    dftoi['TOI'] = 'TOI-' + dftoi['TOI'].astype(str)
    dftoi['host'] = 'TIC ' + dftoi['TIC'].astype(str)
      
    # make these not all caps
    dfkoi['koi_disposition'] = dfkoi['koi_disposition'].str.title()
    dfk2['k2c_disp'] = dfk2['k2c_disp'].str.title()
    
    # make KOI strings into the format we expect
    dfkoi['kepoi_name'].replace(to_replace='K0+', value='KOI-',
                                regex=True, inplace=True)
    
    # jupiter/earth radius ratio
    radratio = 11.21
    # give KOIs/TOIs units of Jupiter radii
    dfkoi['koi_pradj'] = dfkoi['koi_prad'] / radratio
    dftoi['pradj'] = dftoi['prade'] / radratio
    
    # K2 tables don't have both columns always filled in
    noearth = (~np.isfinite(dfk2['pl_rade']) & np.isfinite(dfk2['pl_radj']))
    dfk2.loc[noearth, 'pl_rade'] = dfk2.loc[noearth, 'pl_radj'] * radratio
    
    nojup = (np.isfinite(dfk2['pl_rade']) & (~np.isfinite(dfk2['pl_radj'])))
    dfk2.loc[nojup, 'pl_radj'] = dfk2.loc[nojup, 'pl_rade'] / radratio
    
    # set the appropriate discover facility for candidates
    dfkoi['pl_facility'] = 'Kepler'
    dfk2['pl_facility'] = 'K2'
    dftoi['pl_facility'] = 'TESS'
    
    # where do we want to point people to on clicking?
    dfcon['url'] = ('https://exoplanetarchive.ipac.caltech.edu/overview/' + 
                    dfcon['pl_hostname'])
    dfk2['url'] = ('https://exofop.ipac.caltech.edu/k2/edit_target.php?id=' + 
                   dfk2['epic_name'].str.slice(5))
    exo = 'https://exoplanetarchive.ipac.caltech.edu/cgi-bin/Display' \
          'Overview/nph-DisplayOverview?objname='
    dfkoi['url'] = (exo + dfkoi['kepoi_name'].str.slice(0,-3) +
                    '&type=KEPLER_TCE_HOST')
    dftoi['url'] = ('https://exofop.ipac.caltech.edu/tess/target.php?id=' +
                    dftoi['TIC'].astype(str))

    return dfcon, dfkoi, dfk2, dftoi


def log_axis_labels(min_tick=-2.001, max_tick=3.):
    """
    Bokeh can't do subscript or superscript text, which includes scientific
    notation in axis labels. This is a hack script that uses unicode
    superscript values and manually creates pseudo-scientific notation axis
    labels. Any values within log10(min_tick) and log10(max_tick) will be 
    displayed as normal, while outside those bounds in either direction will
    be converted to scientific notation.

    Parameters
    ----------
    min_tick : float, optional
        Maximum small log(10) value that will display in scientific notation
        instead of the full decimal representation. The default is -2.001,
        meaning axis labels will go from 9x10^-3 to 0.01.
    max_tick : float, optional
        Minimum large log(10) value that will display in scientific notation
        instead of the full decimal representation. The default is 3, meaning
        axis labels will go from 999 to 10^3.

    Returns
    -------
    str: 
        JavaScript code function that generates the appropriate tick labels.

    """
    return f"""
var logtick = Math.log10(tick);
if ((logtick > {min_tick}) && (logtick < {max_tick})){{
    return tick.toLocaleString();
}} else {{
    var power = Math.floor(logtick);
    var retval = 10 + (power.toString()
             .split('')
             .map(function (d) {{ return d === '-' ? '⁻' : '⁰¹²³⁴⁵⁶⁷⁸⁹'[+d]; }})
             .join(''));
    var front = (tick/Math.pow(10, power)).toPrecision(2).toString().slice(0,3);
    
    if (front == '1.0'){{
        return retval
    }}
    else if (front.slice(1,3) == '.0'){{
        return front[0] + 'x' + retval
    }}
    
    return front + 'x' + retval
}}
    """
    
    