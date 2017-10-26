import pandas as pd
from functools import reduce
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sqlite3
import os

plt.style.use ('ggplot')

city_flows_dfs = []
metro_flows_dfs = []

data_path = '/Users/anastasiaclark/irs_nyc_migration/data'
db = 'irsmig_county_database'
con = sqlite3.connect (os.path.join (data_path, db, "irs_migration_county.sqlite"))
metros = pd.read_csv (os.path.join (data_path, 'metros', 'metros_basic.csv'),
                      converters={'fips': str, 'co_code': str, 'cbsa_code': str})

years = ['2011_12', '2012_13', '2013_14', '2014_15']  # project years

# add here variables that holdcounties list for other cities
# NYC counties
nyc = ('36005', '36047', '36061', '36081', '36085')

nyma=('34003','34013','34017','34019','34023','34025','34027','34029','34031',\
      '34035','34037','34039','36005','36027','36047','36059','36061','36071',\
      '36079','36081','36085','36087','36103','36119','42103')

foreign=('57005','57009','57001','57003','57007')
suppressed=('58000','59000')



def get_flows_by_city(year, city):
    """ function to read in data from the database
    and select only flows for selected city

    :rtype: dataframe"""

    # read in inflow & outflow data and store it in a pandas dataframe
    table1 = 'outflow_{}'.format (year)
    table2 = 'inflow_{}'.format (year)

    # SQL query to select fl
    # ows between, but not within counties
    df_out = pd.read_sql_query ("SELECT * from {} where {}.origin!={}.destination".format (table1, table1, table1), con)
    df_in = pd.read_sql_query ("SELECT * from {} where {}.origin!={}.destination".format (table2, table2, table2), con)

    # Make the index to be same for same records
    df_out['uid'] = df_out.origin + "_" + df_out.destination
    df_in['uid'] = df_in.origin + "_" + df_in.destination

    df_in.set_index ('uid', inplace=True)
    df_out.set_index ('uid', inplace=True)

    city_in = df_in[(df_in['destination'].isin (city)) & (~df_in['origin'].isin (city))]
    city_out = df_out[(df_out['origin'].isin (city)) & (~df_out['destination'].isin (city))]

    to_city = city_in[['origin', 'co_orig_name', 'exemptions', 'st_orig_abbrv']].groupby (
        ['origin', 'co_orig_name', 'st_orig_abbrv']).sum ().sort_values ('exemptions', ascending=False).reset_index ()
    from_city = city_out[['destination', 'co_dest_name', 'st_dest_abbrv', 'exemptions']].groupby (
        ['destination', 'co_dest_name', 'st_dest_abbrv']).sum ().sort_values ('exemptions',
                                                                              ascending=False).reset_index ()
    to_city.rename (columns={'origin': 'co_fips', 'co_orig_name': 'co_name', 'exemptions': 'inflow' + year,
                             'st_orig_abbrv': 'state'}, inplace=True)
    from_city.rename (columns={'destination': 'co_fips', 'co_dest_name': 'co_name', 'st_dest_abbrv': 'state',
                               'exemptions': 'outflow' + year}, inplace=True)

    flows_city = to_city.merge (from_city, on=['co_fips', 'co_name', 'state'], how='outer')

    # merge metro areas info to nyc flows to determine which counties from these flows are urban
    flows_city = flows_city.merge (metros[['cbsa_code', 'cbsa_name', 'fips']], left_on='co_fips', right_on='fips',
                                   how='left').drop ('fips', 1)
    
    # label counties that are nor part of the metro areas and are not supressed or foregin as non-metro counties
    flows_city.loc[(~flows_city['co_fips'].isin(suppressed)) & (~flows_city['co_fips'].isin(foreign)) & (flows_city['cbsa_code'].isnull()),['cbsa_name']]='non-metro'
    
    # add calculated columns
    flows_city['net_flow' + year] = flows_city['inflow' + year] - flows_city['outflow' + year]
    #flows_city['in_ratio' + year] = flows_city['inflow' + year] / flows_city['outflow' + year]
    return flows_city


######################################################################################################

# this part is specific to NYC/NY metro , but can be repeated for any other city/metro

# run the functions to get inflow/outflow data for New York city and for NY metro area
# for each year and append the results to a list
for year in years:
    city_flows_dfs.append (get_flows_by_city (year, nyc))

for year in years:
    metro_flows_dfs.append (get_flows_by_city (year, nyma))

# merge all years dfs for NYC (Metro) from the list into a single df
city_flows=reduce(lambda x, y: pd.merge(x, y, on = ['co_fips', 'co_name', 'state', 'cbsa_code', 'cbsa_name'], how='outer'), city_flows_dfs)
metro_flows=reduce(lambda x, y: pd.merge(x, y, on = ['co_fips', 'co_name', 'state', 'cbsa_code', 'cbsa_name'], how='outer'), metro_flows_dfs)

# create table of flows grouped by metro area
grouped_by_metro=metro_flows.groupby('cbsa_name').sum()

# get a list of net_flow columns--needs to be recalculated
net_cols=[c for c in grouped_by_metro.columns if 'net_flow' in c]
for col in net_cols:
    yr = col[-7:]
    grouped_by_metro[col]= grouped_by_metro['inflow' + yr] - grouped_by_metro['outflow' + yr]
    
# create ranks for inflow and outflow for each year
city_flows.fillna (0, inplace=True)
metro_flows.fillna(0, inplace=True)
for col in [c for c in city_flows.columns if 'inflow' in c or 'outflow' in c]:
    yr = col[-7:]
    in_out = col[0:2]
    city_flows['{}_rank{}'.format (in_out, yr)] = city_flows[col].rank (method='dense', ascending=False)
    metro_flows['{}_rank{}'.format (in_out, yr)] = metro_flows[col].rank (method='dense', ascending=False)


# write the resulting data out to use for mapping in QGIS 
# city_flows.to_csv('yrs_2011_2015_nyc_mig_by_county.csv')
# metro_flows.to_csv('yrs_2011_2015_ny_mig_by_metro.csv')

# get top senders/receivers
# counties that were ranked as top 5 (top 10) senders/receivers in any of the four years periods
# plots
    
domestic_city_flows=city_flows[~city_flows['co_fips'].isin (foreign)].copy()
foreign_city_flows=city_flows[city_flows['co_fips'].isin (foreign)].copy()

domestic_metro_flows=metro_flows[~metro_flows['co_fips'].isin (foreign)].copy()
foreign_metro_flows=metro_flows[metro_flows['co_fips'].isin (foreign)].copy()

# number of top places that send/receive movers to/from NYC/NYMA
top =10

def get_top_senders(df):
    all_time_top_senders = \
        df[
            (df['in_rank2011_12'] <= top) | (df['in_rank2012_13'] <= top) | (
                df['in_rank2013_14'] <= top) | (
                df['in_rank2014_15'] <= top)].copy()

    return all_time_top_senders
    
def get_top_receivers(df):    
    all_time_top_receivers = \
        df[
            (df['ou_rank2011_12'] <= top) | (df['ou_rank2012_13'] <= top) | (
                df['ou_rank2013_14'] <= top) | (df['ou_rank2014_15'] <= top)].copy()

    return all_time_top_receivers

top_senders_to_nyc=get_top_senders(domestic_city_flows)
top_senders_to_nyc['county'] = top_senders_to_nyc['co_name'] + "," + top_senders_to_nyc['state']
top_senders_to_nyc = top_senders_to_nyc.set_index ('county').drop (['co_name', 'state'], 1)

top_receivers_from_nyc=get_top_receivers(domestic_city_flows)
top_receivers_from_nyc['county'] = top_receivers_from_nyc['co_name'] + "," + top_receivers_from_nyc['state']
top_receivers_from_nyc = top_receivers_from_nyc.set_index ('county').drop (['co_name', 'state'], 1)

def plot_ranks(df, cols, title):

    """function to plot change in ranks over time
    :param df: dataframe to plot
    :param cols: a list of colum ranks to plot 
    :param title: Tile to display
    """
    df_ranks=df[cols]
    df_ranks.columns = [col[-7:] if 'rank' in col else col for col in df_ranks.columns]
    ax = df_ranks.T.plot (marker='o')
    ax.invert_yaxis ()
    ax.yaxis.set_major_locator (ticker.MaxNLocator (integer=True)) # display only whole numbers
    ax.set_ylim([df_ranks.max().max(),1])
    ax.legend (bbox_to_anchor=(1.07, 1), loc='upper left')
    ax.set_xlabel ('Year')
    ax.set_ylabel ('Rank')
    ax2 = ax.twinx () # get second y axis on the right
    ax2.yaxis.set_major_locator (ticker.MaxNLocator (integer=True))
    ax2.set_ylim (ax.get_ylim ())
    plt.title (title)
    plt.show ()



plot_ranks (top_senders_to_nyc,['in_rank2011_12', 'in_rank2012_13', 'in_rank2013_14', 'in_rank2014_15'], 'Change in Ranks for Top Migrant Senders to NYC')
plot_ranks (top_receivers_from_nyc,['ou_rank2011_12', 'ou_rank2012_13', 'ou_rank2013_14', 'ou_rank2014_15'], 'Change in Ranks for Top Migrant Receivers from NYC')


def get_total_flows(df):
  in_mig=pd.DataFrame(df[['inflow2011_12','inflow2012_13','inflow2013_14','inflow2014_15']].sum(axis=0), columns=['in_migration']).reset_index().rename(columns={'index':'years'})
  in_mig['years']=in_mig.years.apply(lambda x :x[-7:])
  out_mig=pd.DataFrame(df[['outflow2011_12','outflow2012_13','outflow2013_14','outflow2014_15']].sum(axis=0), columns=['out_migration']).reset_index().rename(columns={'index':'years'})
  out_mig['years']=out_mig.years.apply(lambda x :x[-7:])
  df_total=pd.merge(in_mig,out_mig, on='years')
  df_total['net_migration']=df_total['in_migration']-df_total['out_migration']
  df_total.set_index('years',inplace=True)  
  return df_total

total_city_foreign=get_total_flows(foreign_city_flows)
total_city_dom=get_total_flows(domestic_city_flows)

total_metro_dom=get_total_flows(domestic_metro_flows)
total_metro_foreign=get_total_flows(foreign_metro_flows)

def plot_migration(df, title):
    ax=df[['in_migration','out_migration']].plot(rot=0, legend=False, color=['#A0CCCF','#FFB834'])
    df['net_migration'].plot(kind='bar', ax=ax, rot=0, color='#006944', width=0.2)
    ax.legend (bbox_to_anchor=(1.07, 1), loc='upper left')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax.set_title(title)
    plt.show()
  
plot_migration(total_city_dom, 'NYC Domestic Migration, 2011-2014')
plot_migration(total_city_foreign,'NYC International Migration, 2011-2014')

plot_migration(total_metro_dom, 'New York Metro Domestic Migration, 2011-2014')
plot_migration(total_metro_foreign,'New York Metro International Migration, 2011-2014')


grouped_by_metro=metro_flows.groupby('cbsa_name').sum()
# to do display cummulative on the plot