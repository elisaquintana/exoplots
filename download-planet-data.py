"""Downloads candidate and confirmed planet tables from NExSci"""
import pandas as pd
from datetime import datetime

NEXSCI_API = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph' \
             '-nstedAPI'

# The "exoplanets" table includes all confirmed planets and hosts in the
# archive with parameters derived from a single, published reference

# All confirmed planets
print('Downloading all confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*')
df.to_csv('data/confirmed-planets.csv')

# full KOI table
print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*')
df.to_csv('data/kepler-kois-full.csv')

# grab all the K2 candidates (or at least the ones they have put into this
# not-quite-complete table)
print('Downloading full K2 candidates table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*')
df.to_csv('data/k2-candidates-table.csv')

# get the TOI list from ExoFOP-TESS.
print('Downloading full TESS candidates table from ExoFOP...')
df = pd.read_csv('https://exofop.ipac.caltech.edu/tess/download_toi.php?sort'
                 '=toi&output=csv')
df.to_csv('data/tess-candidates.csv')

with open('data/last_update_time.txt', 'w') as ff:
    ff.write(str(datetime.now()))

"""
# all old KOI releases. Should only have to download these once
print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q17_dr25_sup_koi&select=*')
df.to_csv('data/kepler-kois-q1_q17_dr25_sup.csv')


print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q17_dr25_koi&select=*')
df.to_csv('data/kepler-kois-q1_q17_dr25.csv')


print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q17_dr24_koi&select=*')
df.to_csv('data/kepler-kois-q1_q17_dr24.csv')


print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q16_koi&select=*')
df.to_csv('data/kepler-kois-q1_q16_koi.csv')


print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q12_koi&select=*')
df.to_csv('data/kepler-kois-q1_q12_koi.csv')

print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q8_koi&select=*')
df.to_csv('data/kepler-kois-q1_q8_koi.csv')


print('Downloading full KOI table from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=q1_q6_koi&select=*')
df.to_csv('data/kepler-kois-q1_q6_koi.csv')
"""
