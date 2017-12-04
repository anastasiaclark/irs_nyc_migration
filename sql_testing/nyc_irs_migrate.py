#Frank Sept 25, 2017
#Create formatted text tables and csvs from irs migration database for NYC
#Used to verify county results from Jupyter Notebook
#Set first time: path to database
#Change each time: outfolder, target, series labels

from prettytable import PrettyTable
import sqlite3, csv, os

def dosql(series,sql,label):
    curs.execute(sql)
    colnames=[cn[0] for cn in curs.description]
    rows = curs.fetchall()
    x = PrettyTable(colnames)
    x.padding_width = 1
    for row in rows:
        x.add_row(row)
    print (series,":",tab)
    print (x)
    print('\n')
    tabstring = x.get_string()

    txtfile=os.path.join(outfolder,'tables',label+'.txt')

    txtoutput=open(txtfile,'w')
    txtoutput.write(series+'\n')
    txtoutput.write(label+'\n')
    txtoutput.write(tabstring)
    txtoutput.close()

    csvfile=os.path.join(outfolder,'csv',label+'.csv')
    with open(csvfile,'w', newline='') as csvoutput:
        writer=csv.writer(csvoutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(colnames)
        writer.writerows(rows)
    print('* Created tables for ',series, label,'\n')

#Change outfolder to a title that reflects what the data is
outfolder='nyc'
if not os.path.exists(outfolder):
    os.makedirs(os.path.join(outfolder,'tables'))
    os.makedirs(os.path.join(outfolder,'csv'))
    
#Set first time - path to database
data_path = '/home/franknitty/irs_nyc_migration/data'
db = 'irsmig_county_database'
sqldb=os.path.join(data_path,db,'irs_migration_county.sqlite')
#Change target to FIPS code geographies to process
target="('36005','36047','36061','36081','36085')" #this is nyc
#target="('06037')" #this is la

tabs_inflow=['inflow_2014_15','inflow_2013_14','inflow_2012_13','inflow_2011_12']
tabs_outflow=['outflow_2014_15','outflow_2013_14','outflow_2012_13','outflow_2011_12']
tabs_inout=list(zip(tabs_inflow,tabs_outflow))

tabs_intotal=list((item+'_totals' for item in tabs_inflow))
tabs_outtotal=list((item+'_totals' for item in tabs_outflow))
tabs_net=list(zip(tabs_intotal,tabs_outtotal))

#Inflows
sql1='SELECT origin, st_orig_abbrv, co_orig_name, sum(returns) AS returns, sum(exemptions) AS exempts \
FROM %s WHERE destination IN %s AND origin NOT IN %s GROUP BY origin, st_orig_abbrv, co_orig_name \
ORDER BY sum(exemptions) DESC'

#Outflows
sql2='SELECT destination, st_dest_abbrv, co_dest_name, sum(returns) AS returns, sum(exemptions) AS exempts \
FROM %s WHERE origin IN %s AND destination NOT IN %s GROUP BY destination, st_dest_abbrv, co_dest_name \
ORDER BY sum(exemptions) DESC'

#Net change
sql3="SELECT county, stname, coname, sum(returns) AS returns, sum(exempts) AS exempts FROM \
(SELECT origin AS county, st_orig_abbrv AS stname, co_orig_name AS coname, \
sum(returns) AS returns, sum(exemptions) AS exempts \
FROM %s WHERE destination IN %s AND origin NOT IN %s \
GROUP BY origin \
UNION \
SELECT destination AS county,st_dest_abbrv AS stname, co_dest_name AS coname,\
sum(returns)*-1 AS returns, sum(exemptions)*-1 AS exempts \
FROM %s WHERE origin IN %s AND destination NOT IN %s \
GROUP BY destination) \
GROUP BY county ORDER BY exempts DESC"

#Summary net change
sql4="SELECT i.origin, sum(i.returns - o.returns) AS Net_Change_Returns,\
sum(i.exemptions - o.exemptions) AS Net_Change_Exempts \
FROM %s AS i JOIN %s AS o \
WHERE i.uid = o.uid \
AND i.origin LIKE '9%%' AND i.destination IN %s \
AND o.destination LIKE '9%%' AND o.origin IN %s GROUP BY i.origin"

con=sqlite3.connect(sqldb)
curs=con.cursor()

#Change the series labels to reflect the geography for the table

for tab in tabs_inflow:
    statement=sql1 %(tab,target,target)
    dosql('NYC In Migration',statement,tab)

for tab in tabs_outflow:
    statement=sql2 %(tab,target,target)
    dosql('NYC Out Migration',statement,tab)

for tab in tabs_inout:
    statement=sql3 %(tab[0], target, target, tab[1], target, target)
    dosql('NYC Net Migration',statement,str(tab[0])+'_'+str(tab[1]))

for tab in tabs_net:
    statement=sql4 %(tab[0], tab[1], target, target)
    dosql('NYC Total Net Migration',statement,str(tab[0])+'_'+str(tab[1]))
    
con.close()
