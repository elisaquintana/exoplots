import numpy as np

from utils import load_data




# load the data
dfcon, dfkoi, dfk2, dftoi = load_data()



# check that we're including all K2 planets, but only counting them once
k2con = dfk2['k2c_disp'] == 'Confirmed'
k2can = dfk2['k2c_disp'] == 'Candidate'

# all K2 confirmed planets are already in the confirmed planets table
notfound = ~np.in1d(dfk2['pl_name'][k2con], dfcon['pl_name'])
assert notfound.sum() == 0

# anything with a planet name in the K2 table but still a candidate hasn't 
# already shown up in the confirmed planets table
hasname = ~dfk2['pl_name'][k2can].isna()
assert np.in1d(dfk2['pl_name'][k2can][hasname], dfcon['pl_name']).sum() == 0

# also test explicitly by RA/Dec/Period

# all these just have very slight differences in period (< 0.2 days) or are
# off by factors of 2 since different groups found different things for the
# same planet
k2exclude = ['EPIC 201505350.01', 'EPIC 201596316.01', 'EPIC 201629650.01',
             'EPIC 201637175.01', 'EPIC 201647718.01', 'EPIC 203771098.01',
             'EPIC 206348688.02', 'EPIC 210968143.01', 'EPIC 212394689.02',
             'EPIC 212672300.01']

# XXX: until this is fixed (the Kruse and Helller .03 are different planets):
k2exclude.append('EPIC 201497682.03')

# make sure all confirmed K2 planets are in the confirmed table exactly once
for index, icon in dfk2[k2con].iterrows():
    res = np.where((np.abs(dfcon['ra'] - icon['ra']) < 1./60)  &
             (np.abs(dfcon['dec'] - icon['dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - icon['pl_orbper']) < 1./60))[0]
    if len(res) != 1:
        # special cases I know about that we can ignore
        assert icon['epic_candname'] in k2exclude
            
# 202126849.01 is HAT-P-54, 212555594.02 is K2-192
# EPIC 201357835.01 is K2-245, but that has a different EPIC (201357643)
k2exclude2 = ['EPIC 202126849.01', 'EPIC 212555594.02', 'EPIC 201357835.01']   

# make sure all candidate K2 planets aren't in the confirmed table
for index, ican in dfk2[k2can].iterrows():
    res = np.where((np.abs(dfcon['ra'] - ican['ra']) < 1./60)  &
             (np.abs(dfcon['dec'] - ican['dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - ican['pl_orbper']) < 1./60))[0]
    if len(res) != 0:
        # special cases I know about that we can ignore
        assert ican['epic_candname'] in k2exclude2
        # print('K2 PC in confirmed table:', ican['epic_candname'])
        # print(dfcon['pl_name'][res])

# there's not an easy way to tie confirmed planets in the KOI table to entries
# in the confirmed planets table. instead match by RA/Dec/Period
koicon = dfkoi['koi_disposition'] == 'Confirmed'
koican = dfkoi['koi_disposition'] == 'Candidate'

# all these just have very slight differences in period (< 0.2 days)
# which my conservative selection rejects but are good enough
# (KOI-4441 and 5475 was a KOI at half the period of the confirmed planet and 
# 5568 a KOI at 1/3 the confirmed period)
excluded = ['KOI-806.01', 'KOI-806.03', 'KOI-142.01', 'KOI-1274.01',
            'KOI-1474.01', 'KOI-1599.01', 'KOI-377.01', 'KOI-377.02',
            'KOI-4441.01', 'KOI-5568.01', 'KOI-5475.01', 'KOI-5622.01']

# make sure all confirmed KOIs are in the confirmed table exactly once
for index, icon in dfkoi[koicon].iterrows():
    res = np.where((np.abs(dfcon['ra'] - icon['ra']) < 1./60)  &
             (np.abs(dfcon['dec'] - icon['dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - icon['koi_period']) < 1./60))[0]
    if len(res) != 1:
        # special cases I know about that we can ignore
        assert icon['kepoi_name'] in excluded

# make sure all candidate KOIs aren't in the confirmed table
for index, ican in dfkoi[koican].iterrows():
    res = np.where((np.abs(dfcon['ra'] - ican['ra']) < 1./60)  &
             (np.abs(dfcon['dec'] - ican['dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - ican['koi_period']) < 1./60))[0]
    assert len(res) == 0





# there's not an easy way to tie confirmed planets in the TOI table to entries
# in the confirmed planets table. instead match by RA/Dec/Period
toicon = dftoi['disp'] == 'Confirmed'
toican = dftoi['disp'] == 'Candidate'

# make sure all confirmed TOIs are in the confirmed table exactly once
for index, icon in dftoi[toicon].iterrows():
    res = np.where((np.abs(dfcon['ra'] - icon['RA']) < 1./60)  &
             (np.abs(dfcon['dec'] - icon['Dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - icon['period']) < 1./60))[0]
    if len(res) != 1:
        print(icon['TOI'], len(res))
        # special cases I know about that we can ignore
        # assert icon['TOI'] in excluded
print('break')
# make sure all candidate TOIs aren't in the confirmed table
for index, ican in dftoi[toican].iterrows():
    res = np.where((np.abs(dfcon['ra'] - ican['RA']) < 1./60)  &
             (np.abs(dfcon['dec'] - ican['Dec']) < 1./60) & 
             (np.abs(dfcon['pl_orbper'] - ican['period']) < 1./60))[0]
    #assert len(res) == 0
    if len(res) != 0:
        print(ican['TOI'], dfcon['pl_name'][res])






