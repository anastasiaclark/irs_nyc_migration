# Some questions I have

* What do we want to show in graphs? Change over time in the top counties/metros that send/recieve migrants from NYC?
- I think that we initially want to see if the top senders and receivers have consistently remained the same over the four year time period, and if so we can think about showing the total 4-year relative share for inflow, outflow, and net change. Pie / dougnuts for share or bar charts for the top places that show in, out, and net? We can look at the reports from Philly and DC (uploaded the latter today) and the older one from NYC to see how they presented it. Ultimately I think tables will be the most important - we'll have to decide whether to show top 10, 12, or 20 places, and at the county level if we want to break out NYC metro counties from non-metros.

Some examples: Fuller2017 paper for DC, Figure 1 for graphing census population estimates (which we should do too), can also do a similar figure but for showing total IRS inflows, outflows, and net by year, Figures 11 and 12 for net receivers and senders. Pew2010 and Pew2016 papers for Philly, for tables at city-level breaking out suburban counties from cities across the country, dougnuts maybe for illustrating share.

* Do we want to make flow maps or something else? 
  I did circular plots like in [this paper](http://www.global-migration.info/VID%20WP%20Visualising%20Migration%20Flow%20Data%20with%20Circular%20Plots.pdf) for Deborah's migration in Mexico paper. 
  But, I used R scrips described in the paper. So maybe not something you'd want but the paper has other tradtional flow
  maps that could be looked at.
- I'm not sure; those flow maps can be difficult to read. It may be more effective to have a map that shades in the top senders and receivers, similar to the maps in the DC report - they look a bit dull but we can improve the design. 

* Some counties changed fips codes during this 4-year period, 
  if we want to track change in migration over time, we need to deal with this somehow.
- It looks like some change to the rural parts of Alaska, and a small town in Virginia that was absorbed by a surrounding county. We should look into it, but I think it will have minimal impact - the flows to / from NYC may be small enough that they're not even disclosed.

* Is there dictionary for Census pop estimates? Most of the fields are self explanatory, but not all. Don't want to      misinterpret them.
- Yes: it's in the literature folder in my box. I created a folder for articles and another for documentation; it's in the
 
## Comments on the script by section

* 1-5: I can understand this part, no problem

* 6-10: Conceptually I understand what you're doing but I have no idea how this works. The database already has a table (cocodes) in it with fips codes and names - why not use it instead of bringing in the extra json file (one apsect of this paper is demonstrating what's in the database)? You would just have to append the IRS specific codes (same state, different state, etc) after you read the table in. In section 10, I've checked the inflow and outflow tables for 2014_15 and can't see a discrepancy for Orleans: there is an Orleans County in Vermont and another one in New York, and there's an Orleans Parish in Louisiana (Louisiana doesn't have counties - parishes are a county equivalent). I'm a bit nervous that we could be losing records in this deduplication. 

* 11-15, 17-19: In spite of the above concerns, the top 5 or 10 records in each output match the results that I generated earlier, so that's good news! It's interesting in 14 that you're basically using python/pandas to replace the SQL statements that I used. We'll have to work on formatting the ratios - something like 787:949 is not readily graspable. 

* 16,20-21: The goal here is to transition from looking at the flows from/to NYC and other counties to looking at flows from/to the NY Metro and other metros (not looking at the flow to/from NYC and other metros). So similar to step 11 we'd create an nymet group with all the counties in the nym metro and look at flows to from the other metros. In doing this we'd also want to capture flows that fall outside of metro areas. I've added the 2015 metro area spreadsheet to our data files - I've also created a scaled down version called metros_basic.csv that eliminates a lot of extra columns and the records for PR.
