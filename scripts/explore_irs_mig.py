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
nyc = ['36005', '36047', '36061', '36081', '36085']


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

    # add calculated columns
    flows_city['net_flow' + year] = flows_city['inflow' + year] - flows_city['outflow' + year]
    flows_city['in_ratio' + year] = flows_city['inflow' + year] / flows_city['outflow' + year]
    return flows_city


def get_flows_by_metro(year, metro):
    """ function to read in data from the database
    and summarize it for selected metro area

    :param year: The year period from the database in the format 'yyyy_yy'
    :param metro: Name of the metro area; 
            can pass only part of the name if the part is unique for metros
            Ex: 'New York' for New York-Newark-Jersey City, NY-NJ-PA
    :return: dataframe of flows by specified metro area
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

    # get the flows by metro area
    # drop a column in each table, so that the columns are the same in both tables
    df_in.drop ('co_orig_name', 1, inplace=True)
    df_out.drop ('co_dest_name', 1, inplace=True)

    # get inflow and outflow into a single table and since most of the records exist in both tables, drop duplicates
    flows = pd.concat ([df_in, df_out], axis=0).drop_duplicates (
        subset=['origin', 'destination', 'returns', 'exemptions'])

    # check if there are any records with duplicated indexes
    if len (flows[flows.index.duplicated ()]) > 0:
        non_matching = flows.index[flows.index.duplicated ()]

        dfs = []
        for ix in non_matching:
            a = flows.loc[ix, ['exemptions', 'returns']]
            d = a.diff ()
            dfs.append (d)
        df = pd.concat (dfs)

        print ('Summary of the unmatched inflow and outflow tables for year:', year)
        print ('Max difference in exemptions', df.exemptions.max ())
        print ('Min difference in exemptions', df.exemptions.min ())
        print ('Max difference in returns', df.returns.max ())
        print ('Min difference in returns', df.returns.min ())
        print (len (flows))
        flows = flows[~flows.index.duplicated (keep='first')]
        print (len (flows))

    # merge metro area information twice: for county of origin and for county of destination
    flows = flows.merge (metros[['fips', 'cbsa_code', 'cbsa_name']], left_on='destination', right_on='fips',
                         how='left').drop ('fips', 1).rename (
        columns={'cbsa_name': 'dest_name', 'cbsa_code': 'dest_cbsa'})
    flows = flows.merge (metros[['fips', 'cbsa_code', 'cbsa_name']], left_on='origin', right_on='fips',
                         how='left').drop ('fips', 1).rename (
        columns={'cbsa_name': 'orig_name', 'cbsa_code': 'orig_cbsa'})

    # groupby metro of origin and destination to get flows b/n metro areas
    flows_metro = flows[['orig_cbsa', 'orig_name', 'dest_cbsa', 'dest_name', 'returns', 'exemptions']].groupby (
        ['orig_cbsa', 'orig_name', 'dest_cbsa', 'dest_name']).sum ().reset_index ()

    metro_in = flows_metro[(flows_metro.dest_name.str.contains (metro)) & (
        ~flows_metro.orig_name.str.contains (metro))].copy ()  # get all the inter-metro inflows
    metro_out = flows_metro[(flows_metro.orig_name.str.contains (metro)) & (
        ~flows_metro.dest_name.str.contains (metro))].copy ()  # get all the inter-metro outflows

    # rename columns for merging inflow and outflow tables together
    metro_in = metro_in[['orig_cbsa', 'orig_name', 'exemptions']].rename (
        columns={'orig_cbsa': 'cbsa_code', 'orig_name': 'cbsa_name', 'exemptions': 'inflow' + year})
    metro_out = metro_out[['dest_cbsa', 'dest_name', 'exemptions']].rename (
        columns={'dest_cbsa': 'cbsa_code', 'dest_name': 'cbsa_name', 'exemptions': 'outflow' + year})

    # merge inflow and outflow by metro into a single table
    by_metro = pd.merge (metro_in, metro_out, on=['cbsa_code', 'cbsa_name'], how='outer')

    # add calculated columns
    by_metro['net_flow' + year] = by_metro['inflow' + year] - by_metro['outflow' + year]
    return by_metro


# this part is specific to NYC/NY metro , but can be repeated for any other city/metro

# run the functions to get inflow/outflow data for New York city and for NY metro area
# for each year and append the results to a list
for year in years:
    city_flows_dfs.append (get_flows_by_city (year, nyc))

for year in years:
    metro_flows_dfs.append (get_flows_by_metro (year, 'New York'))

# merge all years dfs for NYC (Metro) from the list into a single df
city_flows=reduce(lambda x, y: pd.merge(x, y, on = ['co_fips', 'co_name', 'state', 'cbsa_code', 'cbsa_name'], how='outer'), city_flows_dfs)
metro_flows=reduce(lambda x, y: pd.merge(x, y, on = ['cbsa_code', 'cbsa_name'], how='outer'), metro_flows_dfs)


# create ranks for inflow and outflow for each year
# since columns names are the same in metro and city tables, resuse the loop for both tables
city_flows.fillna (0, inplace=True)
metro_flows.fillna (0, inplace=True)
for col in [c for c in city_flows.columns if 'inflow' in c or 'outflow' in c]:
    yr = col[-7:]
    in_out = col[0:2]
    city_flows['{}_rank{}'.format (in_out, yr)] = city_flows[col].rank (method='dense', ascending=False)
    metro_flows['{}_rank{}'.format (in_out, yr)] = metro_flows[col].rank (method='dense', ascending=False)

# write the resulting data out to use for mapping in QGIS 
# city_flows.to_csv('yrs_2011_2015_nyc_mig_by_county.csv')
# metro_flows.to_csv('yrs_2011_2015_ny_mig_by_metro.csv')

# get the counties that were ranked as top 5 (top 10) senders/receivers in any of the four years
# do we want to do the same for Metros??

all_time_top_senders = \
    city_flows[['co_name', 'state', 'in_rank2011_12', 'in_rank2012_13', 'in_rank2013_14', 'in_rank2014_15']][
        (city_flows['in_rank2011_12'] < 5) | (city_flows['in_rank2012_13'] < 6) | (
            city_flows['in_rank2013_14'] < 6) | (
            city_flows['in_rank2014_15'] < 6)]
all_time_top_senders['county'] = all_time_top_senders['co_name'] + "," + all_time_top_senders['state']
all_time_top_senders = all_time_top_senders.set_index ('county').drop (['co_name', 'state'], 1)
all_time_top_senders.columns = [col[-7:] for col in all_time_top_senders.columns]

all_time_top_receivers = \
    city_flows[['co_name', 'state', 'ou_rank2011_12', 'ou_rank2012_13', 'ou_rank2013_14', 'ou_rank2014_15']][
        (city_flows['ou_rank2011_12'] < 10) | (city_flows['ou_rank2012_13'] < 10) | (
            city_flows['ou_rank2013_14'] < 10) | (city_flows['ou_rank2014_15'] < 10)]
all_time_top_receivers['county'] = all_time_top_receivers['co_name'] + "," + all_time_top_receivers['state']
all_time_top_receivers = all_time_top_receivers.set_index ('county').drop (['co_name', 'state'], 1)
all_time_top_receivers.columns = [col[-7:] for col in all_time_top_receivers.columns]


def plot_ranks(df, title):

    """function to plot change in ranks over time
    :param df: dataframe to plot
    :param title: Tile to display
    """

    ax = df.T.plot (marker='o')
    ax.invert_yaxis ()
    ax.yaxis.set_major_locator (ticker.MaxNLocator (integer=True)) # display only whole numbers
    ax.legend (bbox_to_anchor=(1.07, 1), loc='upper left')
    ax.set_xlabel ('Year')
    ax.set_ylabel ('Rank')
    ax2 = ax.twinx () # get second y axis on the right
    ax2.yaxis.set_major_locator (ticker.MaxNLocator (integer=True))
    ax2.set_ylim (ax.get_ylim ())
    plt.title (title)
    plt.show ()


plot_ranks (all_time_top_senders, 'Change in Ranks for Top Migrant Senders to NYC')
plot_ranks (all_time_top_receivers, 'Change in Ranks for Top Migrant Receivers from NYC')

# TO DO resolve the issue#2, update jupyter notebook 


def get_total_flows(df):
  in_mig=pd.DataFrame(df[['inflow2011_12','inflow2012_13','inflow2013_14','inflow2014_15']].sum(axis=0), columns=['in_migration']).reset_index().rename(columns={'index':'years'})
  in_mig['years']=in_mig.years.apply(lambda x :x[-7:])
  out_mig=pd.DataFrame(df[['outflow2011_12','outflow2012_13','outflow2013_14','outflow2014_15']].sum(axis=0), columns=['out_migration']).reset_index().rename(columns={'index':'years'})
  out_mig['years']=out_mig.years.apply(lambda x :x[-7:])
  df_total=pd.merge(in_mig,out_mig, on='years')
  df_total['net_migration']=df_total['in_migration']-df_total['out_migration']
  return df_total
  
