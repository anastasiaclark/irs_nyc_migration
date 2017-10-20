#The IRS Migration DB only includes filers who were matched between 2 consecutive years
#This script compares the total number of filers who filed in a year from a separate IRS report
#to the number of matched filers in the database and calculates coverage rates for NYC and NY Metro

import pandas as pd
import sqlite3
import os
import matplotlib

data_path='/home/franknitty/irs_nyc_migration/data/'
data_base='irsmig_county_database/irs_migration_county.sqlite'
sqldb=os.path.join(data_path,data_base)
con=sqlite3.connect(sqldb)

nyc=('36005','36047','36061','36081','36085')
nyma=('34003','34013','34017','34019','34023','34025','34027','34029','34031',\
      '34035','34037','34039','36005','36027','36047','36059','36061','36071',\
      '36079','36081','36085','36087','36103','36119','42103')

years=['2011_12','2012_13','2013_14','2014_15']


#Get sum of filers in the migration db for NY metro by grouping non-migrants and in-migrants
df_nymetmig = pd.DataFrame()

for year in years:
    tab='inflow_{}'.format(year)
    mtotal = pd.read_sql_query('SELECT "{}" AS year, destination AS fips, \
    sum(returns) AS returns,sum(exemptions) AS exemptions \
    FROM {} where destination in {} GROUP BY destination'.format(year,tab,nyma),con)
    df_nymetmig=df_nymetmig.append(mtotal,ignore_index=True)
    
con.close()

#Get total number of all filers from csv
data_csv=os.path.join(data_path,'total_filers/totfilers_nymetro.csv')
df_totalfiler=pd.read_csv((data_csv),converters={'fips':str})

#Join the two tables together
joined=pd.merge(df_totalfiler, df_nymetmig, on=['fips','year'])
joined.rename(columns={'returns_x':'totreturns','exempt':'totexempts',
                       'returns_y':'migreturns','exemptions':'migexempts'},inplace=True)

#Generate summaries and calculate percentages for the NY metro area
nyma_matched=joined[['year','migreturns','totreturns','migexempts','totexempts']].groupby(['year']).sum().reset_index()
nyma_matched['pct_returns']=((nyma_matched.migreturns / nyma_matched.totreturns)*100).round(1)
nyma_matched['pct_exempts']=((nyma_matched.migexempts / nyma_matched.totexempts)*100).round(1)

#Generate summaries and calculate percentages for the NYC
nyc_matched=joined[joined['fips'].isin(nyc)][['year','migreturns','totreturns','migexempts','totexempts']].groupby(['year']).sum().reset_index()
nyc_matched['pct_returns']=((nyc_matched.migreturns / nyc_matched.totreturns)*100).round(1)
nyc_matched['pct_exempts']=((nyc_matched.migexempts / nyc_matched.totexempts)*100).round(1)

#LaTeX example NYC table
print(nyc_matched.to_latex())

#Figure example NYC plot
bchart=pd.DataFrame(nyc_matched.set_index(['year']), columns=['pct_returns','pct_exempts'])
my_plot = bchart.plot(kind='bar',title="Total NYC Filers Included in Migration DB",rot=0)
my_plot.set_xlabel("Year")
my_plot.set_ylabel("% Total")
my_plot.legend(["Returns","Exemptions"], loc=4,ncol=2)

fig = my_plot.get_figure()
fig.savefig('test_figure.png')
