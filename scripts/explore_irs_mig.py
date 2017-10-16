import pandas as pd
import numpy as np
import sqlite3
import os
from fractions import Fraction

def get_ratio(ins,outs):    
    """ Function to display in to out ratio in the format 1:7 """
    if ins==0:
        ratio='0'+':'+str(int(outs))
        return ratio
    elif outs==0:
        ratio=str(int(ins))+':'+'0'
        return ratio
    elif ins==outs:
        ratio='1:1'
        return ratio
    else:
        ratio=str(Fraction(ins/outs).limit_denominator(1000)).split('/')[0]+':'+str(Fraction(ins/outs).limit_denominator(1000)).split('/')[1]
        return ratio

# NYC counties
nyc=['36005','36047','36061','36081','36085']
nyc_flows_dfs=[]
ny_metro_flows_dfs=[]


data_path='/Users/anastasiaclark/irs_nyc_migration/data'
db='irsmig_county_database'
con = sqlite3.connect(os.path.join(data_path,db,"irs_migration_county.sqlite"))
metros=pd.read_csv(os.path.join(data_path,'metros','metros_basic.csv'),converters={'fips':str,'co_code':str,'cbsa_code':str})

years=['2011_12','2012_13','2013_14','2014_15'] # project years 

for year in years:
    table1='outflow_{}'.format(year)
    table2='inflow_{}'.format(year)
    
    df_out = pd.read_sql_query("SELECT * from {} where {}.origin!={}.destination".format(table1, table1, table1), con)
    df_in=pd.read_sql_query("SELECT * from {} where {}.origin!={}.destination".format(table2, table2, table2), con)      

    # Make the index to be same for same records
    df_out['uid']=df_out.origin+"_"+df_out.destination
    df_in['uid']=df_in.origin+"_"+df_in.destination
    df_in.set_index('uid', inplace=True)
    df_out.set_index('uid', inplace=True)
    
    nyc_in=df_in[(df_in['destination'].isin(nyc)) & (~df_in['origin'].isin(nyc))]
    nyc_out=df_out[(df_out['origin'].isin(nyc)) & (~df_out['destination'].isin(nyc))]

    to_nyc=nyc_in[['origin','co_orig_name','exemptions','st_orig_abbrv']].groupby(['origin','co_orig_name','st_orig_abbrv']).sum().sort_values('exemptions',ascending=False).reset_index()
    from_nyc=nyc_out[['destination','co_dest_name','st_dest_abbrv','exemptions']].groupby(['destination','co_dest_name','st_dest_abbrv']).sum().sort_values('exemptions',ascending=False).reset_index()
    to_nyc.rename(columns={'origin':'co_fips','co_orig_name':'co_name','exemptions':'inflow'+year,'st_orig_abbrv':'state'},inplace=True)
    from_nyc.rename(columns={'destination':'co_fips','co_dest_name':'co_name','st_dest_abbrv':'state','exemptions':'outflow'+year},inplace=True)
    flows_nyc = to_nyc.merge(from_nyc, on=['co_fips', 'co_name', 'state'], how='outer')
    # merge metro areas info to nyc flows to determine what counties from thesae flows are urban
    flows_nyc=flows_nyc.merge(metros[['cbsa_name','fips']], left_on='co_fips', right_on='fips', how='left').drop('fips',1)
    # calculate fractions, net flow and ratio
    flows_nyc['net_flow'+year] = flows_nyc['inflow'+year] - flows_nyc['outflow'+year]
    flows_nyc['in_ratio'+year] = flows_nyc['inflow'+year] / flows_nyc['outflow'+year]
    nyc_flows_dfs.append(flows_nyc)
    
    # get the flows by metro area

    # drop a column in each table, so that the columns are the same in both tables
    df_in.drop('co_orig_name',1,inplace=True)
    df_out.drop('co_dest_name',1,inplace=True)

    # get inflow and outflow into a single table and since most of the records exist in both tables, drop duplicates
    flows=pd.concat([df_in,df_out],axis=0).drop_duplicates(subset=['origin','destination','returns','exemptions'])

    # check if there are any records with duplicated indexes
    if len(flows[flows.index.duplicated()])>0:
        non_matching=flows.index[flows.index.duplicated()]
      
        dfs=[]
        for ix in non_matching:
            a=flows.loc[ix,['exemptions','returns']]
            d=a.diff()
            dfs.append(d)
        df=pd.concat(dfs)
        
        print 'Max difference in exemptions', df.exemptions.max()
        print 'Min difference in exemptions',df.exemptions.min()
        print 'Max difference in returns',df.returns.max()
        print 'Min difference in returns',df.returns.min()
        print len(flows)
        flows = flows[~flows.index.duplicated(keep='first')]
        print len(flows)

    # merge metro area information twice: for county of origin and for county of destination
    flows = flows.merge(metros[['fips', 'cbsa_name']],left_on='destination', right_on='fips', how='left').drop('fips',1).rename(columns={'cbsa_name':'dest_cbsa'})
    flows = flows.merge(metros[['fips', 'cbsa_name']],left_on='origin', right_on='fips', how='left').drop('fips',1).rename(columns={'cbsa_name':'orig_cbsa'})

    # groupby metro of origin and destination to get flows b/n metro areas
    metro_flows=flows[['orig_cbsa','dest_cbsa','returns','exemptions']].groupby(['orig_cbsa','dest_cbsa']).sum().reset_index()

    ny_metro_in=metro_flows[(metro_flows.dest_cbsa.str.contains('New York')) & (~metro_flows.orig_cbsa.str.contains('New York'))].copy()
    ny_metro_out=metro_flows[(metro_flows.orig_cbsa.str.contains('New York')) & (~metro_flows.dest_cbsa.str.contains('New York'))].copy()
    
    ny_metro_in=ny_metro_in[['orig_cbsa','exemptions']].rename(columns={'orig_cbsa':'metro_name','exemptions':'inflow'+year})
    ny_metro_out=ny_metro_out[['dest_cbsa','exemptions']].rename(columns={'dest_cbsa':'metro_name','exemptions':'outflow'+year})


    ny_by_metro=pd.merge(ny_metro_in, ny_metro_out, on='metro_name', how='outer')

    # since some metro areas don't send or don't recieve migrants from NY metro, replace NaN with 0
    ny_by_metro.fillna(0,inplace=True)
    ny_by_metro['net_flow'+year]=ny_by_metro['inflow'+year]-ny_by_metro['outflow'+year]
    ny_metro_flows_dfs.append(ny_by_metro)
   
current=nyc_flows_dfs[0]
for df in nyc_flows_dfs[1:]: 
    current=current.merge(df, left_on=['co_fips','co_name','state', 'cbsa_name'], right_on=['co_fips','co_name','state','cbsa_name'], how='outer')    
current.to_csv('yrs_2011_2015_nyc_mig_by_county.csv')


current=ny_metro_flows_dfs[0]
for df in  ny_metro_flows_dfs[1:]: 
    current=current.merge(df, left_on=['metro_name'], right_on=['metro_name'], how='outer')    
current.to_csv('yrs_2011_2015_ny_mig_by_metro.csv') 

    