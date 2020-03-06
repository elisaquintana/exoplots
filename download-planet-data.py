"""Downloads candidate and confirmed planet tables from NExSci"""
import pandas as pd

NEXSCI_API = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI'

# The "exoplanets" table includes all confirmed planets and hosts in the
# archive with parameters derived from a single, published reference

# All planets
print('Downloading all confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*')
df.to_csv('data/confirmed-planets.csv')

# All Kepler planets
print('Downloading Kepler confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_kepflag>0')
df.to_csv('data/kepler-confirmed-planets.csv')

# All K2 planets
print('Downloading K2 confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_k2flag>0')
df.to_csv('data/k2-confirmed-planets.csv')

# All TESS planets
print('Downloading TESS confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_facility+like+%27TESS%27')
df.to_csv('data/tess-confirmed-planets.csv')


# The "cumulative" table includes all Kepler Objects of Interest (planet candidates)
# Note koi_disposition is the *archive* disposition.
# Here we are including CANDIDATE only (and excluding FALSE POSITIVE and CONFIRMED)
print('Downloading Kepler candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*'
                 '&where=koi_disposition+like+%27CANDIDATE%27')
df.to_csv('data/kepler-candidate-only-planets.csv')

# Here we are including CONFIRMED and CANDIDATE (and excluding FALSE POSITIVE)
print('Downloading Kepler confirmed and candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*'
                 '&where=koi_disposition+like+%27C%25%27')
df.to_csv('data/kepler-confirmed-and-candidate-planets.csv')

# full KOI table
print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*')
df.to_csv('data/kepler-kois-full.csv')


# The 'k2candidates' table includes all K2 planet candidates.
# Note: k2c_disp is the *archive* disposition
# Here we are including CANDIDATES (and excluding FALSE POSITIVE and CONFIRMED)
print('Downloading K2 candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*'
                 '&where=k2c_disp+like+%27CANDIDATE%27+and+k2c_recentflag=1')
df.to_csv('data/k2-candidate-only-planets.csv')

# Here we are including CANDIDATES and CONFIRMED (and excluding FALSE POSITIVE)
print('Downloading K2 confirmed and candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*'
                 '&where=k2c_disp+like+%27C%25%27+and+k2c_recentflag=1')
df.to_csv('data/k2-confirmed-and-candidate-planets.csv')

print('Downloading full K2 candidates table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*')
df.to_csv('data/k2-candidates-table.csv')

# The "k2targets" table
#print('Downloading K2 targets from NExSci...')
#df = pd.read_csv(NEXSCI_API + '?table=k2targets&select=*')
#df.to_csv('data/k2-targets.csv')

# get the TOI list from ExoFOP-TESS.
print('Downloading full TESS candidates table from ExoFOP...')
df = pd.read_csv('https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv')
df.to_csv('data/tess-candidates.csv')


# Later we will include TESS candidates but will need to pull from ExoFOP/TFOP
#
# wget "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets&select=*&where=pl_facility like '%TESS%'" -O "tess-confirmed-planets.csv"

# Current line count as of Feb 21, 2020
#       4127 confirmed-planets.csv
#     892 k2-candidate-only-planets.csv
#    1236 k2-confirmed-and-candidate-planets.csv
#     431 k2-confirmed-planets.csv
#    2421 kepler-candidate-only-planets.csv
#    4724 kepler-confirmed-and-candidate-planets.csv
#    2357 kepler-confirmed-planets.csv
#      42 tess-confirmed-planets.csv
