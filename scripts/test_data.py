from utils import load_data


def get_discovery_year():
    """
    Simultaneously test the data to make sure we're counting each planet
    exactly once and also set up the necessary links between planets on the
    different tables to get year of discovery instead of year of confirmation
    that is listed in the confirmed planets table.
    """
    from glob import glob
    import numpy as np
    import pandas as pd

    # load the data
    dfcon, dfkoi, dfk2, dftoi = load_data()

    # set up the appropriate columns
    dfcon['year_disc'] = dfcon['pl_disc'] * 1
    dfk2['year_disc'] = dfk2['year'] * 1
    dfkoi['year_disc'] = 1950
    dftoi['year_disc'] = dftoi['year'] * 1

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

    # XXX: until this is fixed (the Kruse and Helller .03 are different planets)
    k2exclude.append('EPIC 201497682.03')

    # make sure all confirmed K2 planets are in the confirmed table exactly once
    for index, icon in dfk2[k2con].iterrows():
        res = np.where((np.abs(dfcon['ra'] - icon['ra']) < 1./60) &
                       (np.abs(dfcon['dec'] - icon['dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - icon['pl_orbper']) < 1./60))
        res = res[0]
        if len(res) != 1:
            # special cases I know about that we can ignore
            assert icon['epic_candname'] in k2exclude
            # for now set its discovery year to be late
            icon['year_disc'] = 2050
        else:
            found = dfk2['epic_candname'] == icon['epic_candname']
            k2yr = dfk2['year'][found].min()
            conyr = dfcon.at[res[0], 'pl_disc']
            # set the confirmed planet and this candidate to have the same
            # discovery year
            dfcon.at[res[0], 'year_disc'] = min(k2yr, conyr)
            dfk2.at[index, 'year_disc'] = min(k2yr, conyr)

    # deal with the ones we skipped
    for ival in k2exclude:
        srch = np.where(dfk2['epic_candname'] == ival)[0]
        k2yr = dfk2['year_disc'][dfk2['epic_candname'] == ival].min()
        for isrch in srch:
            dfk2.at[isrch, 'year_disc'] = k2yr
    assert dfk2['year_disc'].max() < 2040

    # 202126849.01 is HAT-P-54, 212555594.02 is K2-192
    # EPIC 201357835.01 is K2-245, but that has a different EPIC (201357643)
    k2exclude2 = ['EPIC 202126849.01', 'EPIC 212555594.02', 'EPIC 201357835.01']

    # make sure all candidate K2 planets aren't in the confirmed table
    for index, ican in dfk2[k2can].iterrows():
        res = np.where((np.abs(dfcon['ra'] - ican['ra']) < 1./60) &
                       (np.abs(dfcon['dec'] - ican['dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - ican['pl_orbper']) < 1./60))
        res = res[0]
        if len(res) != 0:
            # special cases I know about that we can ignore
            assert ican['epic_candname'] in k2exclude2

        found = dfk2['epic_candname'] == ican['epic_candname']
        k2yr = dfk2['year'][found].min()
        dfk2.at[index, 'year_disc'] = k2yr

    # first go through and assign KOIs the year they first showed up in a KOI
    # catalog. We're assuming in this process that a particular KOI number will
    # always refer to the same planet.
    dfkoi['koi_year'] = 1990

    # these first 2 KOI tables aren't archived on Exoplanet Archive
    earlykois = ['data/koi1.txt', 'data/koi2.txt']
    allkois = glob('data/kepler-kois-q*')
    allkois.sort()
    # year the KOI tables were published
    koiyears = [2013, 2014, 2015, 2015, 2016, 2018]

    # load the two early KOI tables. Just use KOI names
    k1 = np.loadtxt(earlykois[0], dtype='<U12', usecols=(0,))
    for ii in np.arange(k1.size):
        k1[ii] = 'KOI-' + k1[ii]

    k2 = np.loadtxt(earlykois[1], dtype='<U12', usecols=(0,), skiprows=73)
    for ii in np.arange(k2.size):
        k2[ii] = 'KOI-' + k2[ii]

    # load the archived KOI tables
    dfs = []
    for ifile in allkois:
        df = pd.read_csv(ifile)
        df['kepoi_name'].replace(to_replace='K0+', value='KOI-',
                                 regex=True, inplace=True)
        dfs.append(df)

    # find the first time a particular KOI number is mentioned and set its year
    for index, row in dfkoi.iterrows():
        ikoi = row['kepoi_name']
        if ikoi in k1 or ikoi in k2:
            dfkoi.at[index, 'koi_year'] = 2011
            continue
        for ii, df in enumerate(dfs):
            if ikoi in df['kepoi_name'].values:
                dfkoi.at[index, 'koi_year'] = koiyears[ii]
                break

    assert dfkoi['koi_year'].min() == 2011 and dfkoi['koi_year'].max() == 2018

    dfkoi['year_disc'] = dfkoi['koi_year'] * 1

    # there's not an easy way to tie confirmed planets in the KOI table to
    # entries in the confirmed planets table. instead match by RA/Dec/Period
    koicon = dfkoi['koi_disposition'] == 'Confirmed'
    koican = dfkoi['koi_disposition'] == 'Candidate'

    # all these just have very slight differences in period (< 0.2 days)
    # which my conservative selection rejects but are good enough
    # (KOI-4441 and 5475 was a KOI at half the period of the confirmed planet
    # and 5568 a KOI at 1/3 the confirmed period)
    excluded = ['KOI-806.01', 'KOI-806.03', 'KOI-142.01', 'KOI-1274.01',
                'KOI-1474.01', 'KOI-1599.01', 'KOI-377.01', 'KOI-377.02',
                'KOI-4441.01', 'KOI-5568.01', 'KOI-5475.01', 'KOI-5622.01']
    # what the name is in the confirmed planets table
    real = ['Kepler-30 d', 'Kepler-30 b', 'KOI-142 b', 'Kepler-421 b',
            'Kepler-419 b', 'KOI-1599.01', 'Kepler-9 b', 'Kepler-9 c',
            'Kepler-1604 b', 'Kepler-1633 b', 'Kepler-1632 b', 'Kepler-1635 b']

    # make sure all confirmed KOIs are in the confirmed table exactly once
    for index, icon in dfkoi[koicon].iterrows():
        res = np.where((np.abs(dfcon['ra'] - icon['ra']) < 1./60) &
                       (np.abs(dfcon['dec'] - icon['dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - icon['koi_period']) < 1/60))
        res = res[0]
        if len(res) != 1:
            # special cases I know about that we can match up manually
            assert icon['kepoi_name'] in excluded
            rname = real[excluded.index(icon['kepoi_name'])]
            res = np.where(dfcon['pl_name'] == rname)[0]
            assert len(res) == 1
        # make sure both tables have the same discovery year
        koiyr = icon['koi_year']
        conyr = dfcon.at[res[0], 'pl_disc']
        dfcon.at[res[0], 'year_disc'] = min(koiyr, conyr)
        dfkoi.at[index, 'year_disc'] = min(koiyr, conyr)

    # make sure all candidate KOIs aren't in the confirmed table
    for index, ican in dfkoi[koican].iterrows():
        res = np.where((np.abs(dfcon['ra'] - ican['ra']) < 1./60) &
                       (np.abs(dfcon['dec'] - ican['dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - ican['koi_period']) < 1/60))
        res = res[0]
        assert len(res) == 0

    # there's not an easy way to tie confirmed planets in the TOI table to
    # entries in the confirmed planets table. instead match by RA/Dec/Period
    toicon = dftoi['disp'] == 'Confirmed'
    toican = dftoi['disp'] == 'Candidate'

    # make sure all confirmed TOIs are in the confirmed table exactly once
    for index, icon in dftoi[toicon].iterrows():
        res = np.where((np.abs(dfcon['ra'] - icon['RA']) < 1./60) &
                       (np.abs(dfcon['dec'] - icon['Dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - icon['period']) < 1./60))[0]
        assert len(res) == 1
        tessyr = icon['year']
        conyr = dfcon.at[res[0], 'pl_disc']
        dfcon.at[res[0], 'year_disc'] = min(tessyr, conyr)
        dftoi.at[index, 'year_disc'] = min(tessyr, conyr)

    # make sure all candidate TOIs aren't in the confirmed table
    for index, ican in dftoi[toican].iterrows():
        res = np.where((np.abs(dfcon['ra'] - ican['RA']) < 1./60) &
                       (np.abs(dfcon['dec'] - ican['Dec']) < 1./60) &
                       (np.abs(dfcon['pl_orbper'] - ican['period']) < 1./60))[0]
        assert len(res) == 0

    return dfcon, dfkoi, dfk2, dftoi


if __name__ == "__main__":
    get_discovery_year()
