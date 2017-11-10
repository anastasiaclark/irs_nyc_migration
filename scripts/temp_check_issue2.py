#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 19:51:05 2017

@author: anastasiaclark
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

cbsa_shape=gpd.read_file('/Users/anastasiaclark/irs_nyc_migration/data/cb_2016_us_cbsa_500k/cb_2016_us_cbsa_500k.shp')
cbsa_mig=pd.read_csv('/Users/anastasiaclark/irs_nyc_migration/scripts/yrs_2011_2015_ny_mig_by_metro.csv', converters={'cbsa_code':str})
metro_data=cbsa_shape.merge(cbsa_mig, left_on='GEOID',right_on='cbsa_code')

metro_data['coords'] = metro_data['geometry'].apply(lambda x: x.representative_point().coords[:])
metro_data['coords'] = [coords[0] for coords in metro_data['coords']]

#metro_data.plot(figsize=(20,20))
#for idx, row in metro_data.iterrows():
#    plt.annotate(s=row['NAME'], xy=row['coords'],
#                 horizontalalignment='center')
#plt.show()  

ax = metro_data.plot()
metro_data.apply(lambda x: ax.annotate(s=x.inflow2011_12, xy=x.coords, ha='center'),axis=1)