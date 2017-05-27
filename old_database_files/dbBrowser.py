################################################
# Looking through ACS database and testing functionality
################################################
import csv
import sqlite3
from collections import OrderedDict


db = sqlite3.connect('../acs/acs.db')

def weighted_averages(db, variable_codes, county_list):
        result = []
        # Calculate weighted average for each variable
        for code in variable_codes:
                total_pop, weighted_sum = 0, 0
                for county in county_list:
                        # Add population of county to total_pop
                        variable_query = "select B01003_001E, {} from acs_data where county = '{}'".format(code, county)
                        variable_query_results = db.execute(variable_query).fetchall()
                        if len(variable_query_results) > 0: # If no data on county, skip
                                county_pop, var_val = variable_query_results[0]
                                if county_pop != '' and var_val != '': # If either population or variable value is missing, ignore
                                        total_pop += float(county_pop)
                                        weighted_sum += float(county_pop)*float(var_val)
                                        
                if total_pop != 0: # If at least one county had non-empty variable value
                        result.append(str(int(weighted_sum/total_pop))) # Round weighted average to nearest int
                else:
                        result.append("n/a")

        return result


variable_query = "pragma table_info(acs_data)"
variable_query_results = db.execute(variable_query).fetchall()
#print variable_query_results

variable_query = "select county, B19013I_001E from acs_data" 
variable_query_results = db.execute(variable_query).fetchall()
#print variable_query_results

county_query = "select county from county_zip where zip = '{}'".format('8873')
county_query_results = db.execute(county_query).fetchall()
print str(county_query_results)
county = str(county_query_results[0][0])
print county
if len(county) < 5:
    for _ in xrange(5-len(county)): county = '0' + county
print county
variable_query = "select {}, county from acs_data where county = '{}'".format('B19013I_001E', county)
variable_query_results = db.execute(variable_query).fetchall()
print variable_query_results



# dict of ACS codes to English fields; uses OrderedDict so the options appear in order on selection box
ACS_VARIABLES = OrderedDict([
	('B03002_001E', 'Hispanic Or Latino Origin By Race Total'),
	('B03002_003E', 'White Alone'),
	('B03002_004E', 'Black Or African American Alone'),
	('B03002_012E', 'Hispanic Or Latino'),
	('B05012_001E', 'Nativity In The United States'),
	('B05012_003E', 'Nativity In The United States (Foreign-Born)'),
	('B01003_001E', 'Total Population'),
	('B05001_001E', 'Nativity And Citizenship Status In The United States Total'),
	('B05001_006E', 'Nativity and Citizenship Status In The United States (Non-Citizen)'),
	('B17001_001E', 'Poverty Status In The Past 12 Months Total'),
	('B17001_002E', 'Income In The Past 12 Months Below Poverty Level'),
	('B17001A_002E', 'Poverty Status In The Past 12 Months Total (White Alone)'),
	('B17001A_001E', 'Income In The Past 12 Months Below Poverty Level (White Alone)'),
	('B17001B_002E', 'Poverty Status In The Past 12 Months Total (Black Or African American Alone)'),
	('B17001B_001E', 'Income In The Past 12 Months Below Poverty Level (Black Or African American Alone)'),
	('B17001I_002E', 'Poverty Status In The Past 12 Months Total (Hispanic Or Latino)'),
	('B17001I_001E', 'Income In The Past 12 Months Below Poverty Level (Hispanic Or Latino)'),
	('B19013_001E', 'Median Household Income In The Past 12 Months'),
	('B19013A_001E', 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (White Alone Householder)'),
	('B19013B_001E', 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Black Or African American Alone Householder)'),
	('B19013I_001E', 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Hispanic Or Latino Householder)'),
	('B19051_001E', 'Earnings In The Past 12 Months For Households Total'),
	('B01002_001E', 'Median Age By Sex Total'),
	('B23025_001E', 'Employment Status For The Population 16 Years And Over Total'),
	('B23025_005E', 'Unemployed'),
	('B23025_003E', 'Civilian Labor Force'),
	('B19083_001E', 'Gini')
])

