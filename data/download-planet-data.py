"""Downloads candidate and confirmed planet tables from NExSci"""
import pandas as pd

NEXSCI_API = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI'

print('Downloading candidate planets from NEXSCI...')
df = pd.read_csv(NEXSCI_API + '?table=cumulative&select=*'
                 '&where=koi_pdisposition+like+%27CANDIDATE%27')
df.to_csv('kepler-candidate-planets.csv')

print('Downloading Kepler confirmed planets from NEXSCI...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_kepflag>0')
df.to_csv('kepler-confirmed-planets.csv')

# Note: k2c_disp is the *archive* disposition, not the paper disposition.
print('Downloading K2 candidate planets from NEXSCI...')
df = pd.read_csv(NEXSCI_API + '?table=k2candidates&select=*'
                 '&where=k2c_disp+like+%27C%25%27')  # +and+k2c_recentflag=1
df.to_csv('k2-candidate-planets.csv')

print('Downloading K2 confirmed planets from NEXSCI...')
df = pd.read_csv(NEXSCI_API + '?table=exoplanets&select=*&where=pl_k2flag>0')
df.to_csv('k2-confirmed-planets.csv')
