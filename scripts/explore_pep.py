# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 16:28:37 2017

@author: anastasiaclark
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')


data_path='/Users/anastasiaclark/irs_nyc_migration/data'
nyc=['36005','36047','36061','36081','36085']

years=['2011','2012','2013','2014','2015', '2016']

metro_pep=pd.read_csv(os.path.join(data_path, 'census_pop_est','cbsa-est2016-modified.csv'))
metro_pep.set_index('CBSA',inplace=True)

county_pep=pd.read_csv(os.path.join(data_path, 'census_pop_est','co-est2016-alldata.csv'), converters={'STATE':str,'COUNTY':str},encoding='LATIN-1')
county_pep['fips']=county_pep.STATE+county_pep.COUNTY
county_pep.set_index('fips',inplace=True)

# most columns are the same in county and metro pep dataset
# however, one column, NPOPCNHG has an underscore in county pep
# remove the udnderscore to make columns of interest be same in both datasets
col_names=[c.replace('_','') for c in county_pep.columns]
county_pep.columns=col_names
county_pep=county_pep.query('COUNTY!="000"').copy()

nyc_est=county_pep.loc[nyc]
ny_metro=metro_pep[metro_pep.NAME.str.contains('New York')].copy()

pop_change=[c for c in nyc_est.columns if c.startswith('NPOPCHG')]
nat_inc=[c for c in nyc_est.columns if c.startswith('NATURALINC')]
net_int=[c for c in nyc_est.columns if c.startswith('INTERNATIONALMIG')]
net_dom=[c for c in nyc_est.columns if c.startswith('DOMESTICMIG')]

keep_cols=pop_change+nat_inc+net_int+net_dom
nyc_est=nyc_est[keep_cols].copy()
ny_metro=ny_metro[keep_cols]

city=nyc_est.sum(axis=0)

def reshape_dataset(df):
    dfs=[]
    for year in years:
        ixs=[i for i in df.index if year in i]
        yr=df.loc[ixs].reset_index().T
        yr.columns=yr.iloc[0]
        yr.drop(yr.index[0], inplace=True)
        yr.index=[year]
        new_names=[n[0:len(n)-4].strip('_') for n in yr.columns]
        yr.columns=new_names
        dfs.append(yr)
    reshaped=pd.concat(dfs)
    return reshaped


def plot_pop_change(df, title):    
    ax=df[['NATURALINC','INTERNATIONALMIG','DOMESTICMIG']].plot(kind='bar',stacked=True)
    df['NPOPCHG'].plot(ax=ax, linestyle=':', color='black', linewidth=3, legend=True)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax.set_title(title)
    plt.show()
    
df1=reshape_dataset(city)    
plot_pop_change(df1, 'NYC Population Change, 2010-2016')   

# top 5 metro areas with largest pop growth
for year in years:
    county_pep[['RNATURALINC{}'.format(year),'RDOMESTICMIG{}'.format(year),'RINTERNATIONALMIG{}'.format(year)]].hist(color='k', alpha=0.5, bins=50,sharey=True)
    print county_pep[['CTYNAME','STNAME','RDOMESTICMIG{}'.format(year)]].sort_values('RDOMESTICMIG{}'.format(year),ascending=False).head(n=10)


def rate_heat_map(rate_col,by_area,title):
    
    '''create a heat map of counties groupoed by
    passed area and fr the passed rate over the years'''
    
    divisions={1 : 'New England', 
            2 : 'Middle Atlantic', 
            3 : 'East North Central',
            4 : 'West North Central', 
            5 : 'South Atlantic', 
            6 : 'East South Central', 
            7 : 'West South Central', 
            8 : 'Mountain', 
            9 : 'Pacific'}     


    regions={1 :'Northeast', 
            2 : 'Midwest', 
            3 : 'South',  
            4 : 'West' }

    cols=county_pep.columns[(county_pep.columns.str.contains(rate_col))|(county_pep.columns.str.contains(by_area))]
    grouped=county_pep[cols].groupby(by_area).mean()
    # get the year on as the column name
    grouped.columns=[c[-4:] for c in grouped.columns]
    
    if by_area=='DIVISION':
        df=pd.Series(divisions).to_frame().rename(columns={0:'division'})
    elif by_area=='REGION':
        df=pd.Series(regions).to_frame().rename(columns={0:'regions'})
        
    grouped=grouped.merge(df, left_index=True, right_index=True).set_index(df.columns[0])
    sns.heatmap(grouped)
    sns.plt.title(title)

    



