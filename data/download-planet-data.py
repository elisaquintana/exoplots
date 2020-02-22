"""Downloads candidate and confirmed planet tables from NExSci"""
import pandas as pd

NEXSCI_API = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI'

# The "exoplanets" table includes all confirmed planets and hosts in the
# archive with parameters derived from a single, published reference

# All planets
print('Downloading all confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*')
df.to_csv('confirmed-planets.csv')

# All Kepler planets
print('Downloading Kepler confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_kepflag>0')
df.to_csv('kepler-confirmed-planets.csv')

# All K2 planets
print('Downloading K2 confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_k2flag>0')
df.to_csv('k2-confirmed-planets.csv')

# All TESS planets
print('Downloading TESS confirmed planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_facility+like+%27TESS%27')
df.to_csv('tess-confirmed-planets.csv')


# The "cumulative" table includes all Kepler Objects of Interest (planet candidates)
# Note koi_disposition is the *archive* disposition.
# Here we are including CANDIDATE only (and excluding FALSE POSITIVE and CONFIRMED)
print('Downloading Kepler candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*'
                 '&where=koi_disposition+like+%27CANDIDATE%27')
df.to_csv('kepler-candidate-only-planets.csv')

# Here we are including CONFIRMED and CANDIDATE (and excluding FALSE POSITIVE)
print('Downloading Kepler confirmed and candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*'
                 '&where=koi_disposition+like+%27C%25%27')
df.to_csv('kepler-confirmed-and-candidate-planets.csv')


# The 'k2candidates' table includes all K2 planet candidates.
# Note: k2c_disp is the *archive* disposition
# Here we are including CANDIDATES (and excluding FALSE POSITIVE and CONFIRMED)
print('Downloading K2 candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*'
                 '&where=k2c_disp+like+%27CANDIDATE%27')
df.to_csv('k2-candidate-only-planets.csv')

# Here we are including CANDIDATES and CONFIRMED (and excluding FALSE POSITIVE)
print('Downloading K2 candidate planets from NExSci...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*'
                 '&where=k2c_disp+like+%27C%25%27')
df.to_csv('k2-confirmed-and-candidate-planets.csv')

# Later we will include TESS candidates but will need to pull from ExoFOP/TFOP
