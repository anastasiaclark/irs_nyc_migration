#Questions to Answer with Tables and Charts

Each of these should be answered twice: one at the NYC and county level, and again at the NYC metro level. 

For questions where we generate either a large list or a small number of summary stats, we just want to see the table or the numbers. For questions where we are looking at years over time or are comparing a handful of places, let's also see a chart.

For maps I think the most logical would be the top net senders / receivers for metro areas in one map. We can try counties too but think it would be less interesting because of clustering around NYC. Could also try raw count of senders / receivers for both counties and metros each in separate maps.

##PEP

- What was the population change (count and rate) for NYC / NYM (year by year and cumulative)? 

- What were the components of change for NYC / NYM (year by year and cumulative)? (look good on chart)

- In terms of population change, how does NYC / NYM rank among other large counties / metros (250k or greater pop?) for the entire (cumulative) period?

- In terms of population change, how does NYM rank among other large metros (250k or greater pop?) for the entire (cumulative) period?

- Among the counties that are home to the 10 biggest cities, how does NYC compare in terms of components of change? (look good on a chart)

- Among the top 10 or 14 biggest metros, how does the NYM metro compare in terms of components of change? (look good on a chart)

##IRS

- What was the number of in-migrants, out-migrants, and net change for domestic migration for NYC / NYM (year by year and cumulative)?

- What was the number of in-migrants, out-migrants, and net change for foreign migration for NYC / NYM (year by year and cumulative)?

- Year by year and cumulatively for domestic migration only, for NYC and NYM, who were the top:
    - Senders (count)
    - Receivers (count)
    - Deficit areas (negative net change)
    - Surplus areas (positive net change)

##10 Biggest Cities

10 is a logical cut-off as all these cities have at least 1 million people. Number 11 (Austin, TX) has 950k versus 10 (San Jose) 1.03mil.

nyc=['36005','36047','36061','36081','36085']
cities=['06037','17031','48201','04013','42101','48029','06073','48113','06085']

06037 Los Angeles, CA (Los Angeles County)
17031 Chicago, IL (Cook County)
48201 Houston, TX (Harris County)
04013 Phoenix, AZ (Maricopa County)
42101 Philadelphia, PA (Philadelphia County)
48029 San Antonio, TX (Bexar County)
06073 San Diego, CA (San Diego County)
48113 Dallas, TX (Dallas County)
06085 San Jose, CA (Santa Clara County)

Anomalies: NYC is the only city that is composed of entire, multiple counties. With the exception of NYC and Philadelphia, all of the cities in this list are located within counties that contain areas that are not part of the city. Small portions of the City of Dallas fall inside other counties that are not included here.

##14 biggest metro areas

14 is a logical cut-off as all these metros have at least 4 million people. Number 15 (Seattle) has 3.8mil versus 14 (Detroit) at 4.3mil. If we wanted a shorter list, next logical cut-off would be at 9; Atlanta has 5.8mil while number 10 Boston has 4.8mil. 

nym=['35620']
metros=['31080','16980','19100','26420','47900','37980','33100','12060','14460','41860','38060','40140','19820']

31080 Los Angeles
16980 Chicago
19100 Dallas
26420 Houston
47900 Washington
37980 Philadelphia
33100 Miami
12060 Atlanta
14460 Boston
41860 San Francisco
38060 Phoenix
40410 Riverside
19820 Detroit



