Data files for New Yorkers on the Move
Frank Donnelly, Anastasia Clark, and Janine Billadello
December, 2017

These summary data files were produced as part of the analysis for the paper "New Yorker's on the Move: Recent Migration Trends for the City and Metro Area" published as part of the Weissman Center for International Business Occasional Paper Series:

http://zicklin.baruch.cuny.edu/centers/weissman/professionals/publications/occasional-papers-series

The code that was written for this analysis, as well as the source and output data, are available on GitHub:

https://github.com/anastasiaclark/irs_nyc_migration

There are three files in this series:

- irs_mig_flows_nyc_2011_15.csv: this data was produced from the IRS SOI county migration data files. The data represent migrant inflows, outflows, and net flows between individual counties and New York City for the years 2011 to 2015. There are columns for each year and aggregate totals for all four years.

- irs_mig_flows_nyma_2011_15.csv: this data was produced from the IRS SOI county migration data files. The data represent migrant inflows, outflows, and net flows between individual metropolitan areas and the New York Metropolitan Area for the years 2011 to 2015. There are columns for each year and aggregate totals for all four years. The metropolitan area definitions are for core based statistical areas (which includes metropolitan and micropolitan areas) defined by the US Office of Management and Budget in July 2015.

- pep_nyma_county_2010_16.csv: this data is an extract of the US Census Bureau's County Population Estimates Data Vintage 2016 that contains one record for each of the counties that are part of the New York Metropolitan Area, based on OMB definitions from July 2015. The first set of columns show the total population for each year. The total population for 2010 is from the 2010 census while the totals for other years are estimates. The following sets of columns show annual change (NPOPCHG) and the annual components of change: natural increase (NATURALINC), foreign migration (INTERNATIONALMIG), and domestic migration (DOMESTICMIG). We modified the 2011 columns from the original source so that they represent change from Apr 1, 2010 to July 1, 2011. The remaining columns show change between July 1 of each year, i.e. 2012 shows change between July 1, 2011 and July 1, 2012. 

Please see the paper for a thorough description of the data and references to the original sources.
