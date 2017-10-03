# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 18:59:18 2017

@author: anastasiaclark
"""

import pandas as pd
import sqlite3
import os
from fractions import Fraction


def get_ratio(ins, outs):
    """ Function to display in to out ratio in the format 1:7 """
    if ins == 0:
        ratio = '0' + ':' + str(int(outs))
        return ratio
    elif outs == 0:
        ratio = str(int(ins)) + ':' + '0'
        return ratio
    elif ins == outs:
        ratio = '1:1'
        return ratio
    else:
        ratio = str(Fraction(ins / outs).limit_denominator(1000)).split('/')[0] + ':' + \
                str(Fraction(ins / outs).limit_denominator(1000)).split('/')[1]
        return ratio


pop_est = pd.read_csv(
    'https://raw.githubusercontent.com/anastasiaclark/irs_nyc_migration/master/data/census_pop_est/co-est2016-alldata.csv?token=AYC98P3jcr5K2cfHCl3LHEi5I6sv_eIQks5Z2qAEwA%3D%3D')
data_path = r'C:\Users\Ernest\Desktop\Anastasia\irs-migration\irs_migration\data\irsmig_county_database'
con = sqlite3.connect(os.path.join(data_path, "irs_migration_county.sqlite"))
counties = pd.read_json(r'C:\Users\Ernest\Desktop\Anastasia\irs-migration\irs_migration\scripts\irs_counties.json',
                        dtype=False)

years = ['2011_12', '2012_13', '2013_14', '2014_15']

# for year in years:
year = years[3]
table1 = 'outflow_{}'.format(year)
table2 = 'inflow_{}'.format(year)

df_out = pd.read_sql_query("SELECT * from {} where {}.origin!={}.destination".format(table1, table1, table1), con)
df_in = pd.read_sql_query("SELECT * from {} where {}.origin!={}.destination".format(table2, table2, table2), con)

# get one master flow table for the year
df_out['uid'] = df_out.origin + "_" + df_out.destination
df_in['uid'] = df_in.origin + "_" + df_in.destination
df_in.set_index('uid', inplace=True)
df_out.set_index('uid', inplace=True)

t_in = df_in.reset_index().merge(counties, left_on='destination', right_on='co_fips', how='left').drop('co_fips',
                                                                                                       1).rename(
    columns={'co_name': 'co_dest_name'}).set_index('uid')
t_out = t = df_out.reset_index().merge(counties, left_on='origin', right_on='co_fips', how='left').drop('co_fips',
                                                                                                        1).rename(
    columns={'co_name': 'co_orig_name'}).set_index('uid')

flows = pd.concat([t_in, t_out], axis=0).drop_duplicates()

con.close()

flows = flows[~flows.index.duplicated(
    keep='first')]  # some counties have slightly different name in in vs out tables Ex: Orleans Parish vs Orelans County

# flows=flows.reset_index().merge(county[['co_fips','metro_name']], left_on='origin', right_on='co_fips', how='left').drop('co_fips',1).rename(columns={'metro_name':'orig_metro'}).set_index('uid')
# flows=flows.reset_index().merge(county[['co_fips','metro_name']], left_on='destination', right_on='co_fips', how='left').drop('co_fips',1).rename(columns={'metro_name':'dest_metro'}).set_index('uid')


ny_metro = 'New York-Newark-Jersey City, NY-NJ-PA'
nyc = ['36005', '36047', '36061', '36081', '36085']

nyc_flows = flows[(flows.origin.isin(nyc)) | (flows.destination.isin(nyc))]

nyc_in = nyc_flows[(nyc_flows['destination'].isin(nyc)) & (~nyc_flows['origin'].isin(nyc))]
nyc_out = nyc_flows[(~nyc_flows['destination'].isin(nyc)) & (nyc_flows['origin'].isin(nyc))]

to_nyc = nyc_in[['origin', 'co_orig_name', 'exemptions', 'st_orig_abbrv']].groupby(
    ['origin', 'co_orig_name', 'st_orig_abbrv']).sum().sort_values('exemptions', ascending=False).reset_index()
from_nyc = nyc_out[['destination', 'co_dest_name', 'st_dest_abbrv', 'exemptions']].groupby(
    ['destination', 'co_dest_name', 'st_dest_abbrv']).sum().sort_values('exemptions', ascending=False).reset_index()
to_nyc.rename(
    columns={'origin': 'co_fips', 'co_orig_name': 'co_name', 'exemptions': 'inflow', 'st_orig_abbrv': 'state'},
    inplace=True)
from_nyc.rename(
    columns={'destination': 'co_fips', 'co_dest_name': 'co_name', 'st_dest_abbrv': 'state', 'exemptions': 'outflow'},
    inplace=True)

county = pd.read_json(r'C:\Users\Ernest\Desktop\Anastasia\irs-migration\irs_migration\data\counties.json', dtype=False)

flows_nyc = to_nyc.merge(from_nyc, on=['co_fips', 'co_name', 'state'], how='outer')

flows_nyc['net_flow'] = flows_nyc.inflow - flows_nyc.outflow
flows_nyc['in_ratio'] = flows_nyc.inflow / flows_nyc.outflow
flows_nyc['out_ratio'] = flows_nyc.outflow / flows_nyc.inflow
flows_nyc.inflow.fillna(0, inplace=True)
flows_nyc.outflow.fillna(0, inplace=True)
flows_nyc['in_to_out_ratio'] = flows_nyc.apply(lambda x: get_ratio(x['inflow'], x['outflow']), axis=1)
flows_nyc = flows_nyc.merge(county[['co_fips', 'metro_name', ]], on='co_fips', how='left')

by_metro = flows_nyc[['metro_name', 'inflow', 'outflow']].groupby('metro_name').sum().sort_values(['inflow', 'outflow'],
                                                                                                  ascending=False)
