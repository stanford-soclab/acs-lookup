################################################
# DATAHELPER MODULE FOR ACS_LOOKUP.PY FLASK APP
################################################
import csv
import sqlite3
from collections import OrderedDict

# TODO add something that checks length of zip and county codes, adds 0 to front if necessary
# TODO why do 4 digit zipcodes not show up?

# checks if filename is .csv
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] == 'csv'

# TODO FUNCTION DESCRIPTION HERE
def weighted_averages(db, variable_codes, county_list):
    #create array for sums over all variables
    total_pop = 0
    weighted_sums = [0]*len(variable_codes)
    for county in county_list:
            # add population of county to total_pop
            variable_query = "select B01003_001E from acs_data where county = '{}'".format(county)
            variable_query_results = db.execute(variable_query).fetchall()
            if len(variable_query_results) > 0:
                    county_pop = float(variable_query_results[0][0])
                    total_pop += county_pop
            else: continue # if can't find total population of county, ignore county
            # add weighted value of variable to weighted_sums
            code_string = ""
            for code in variable_codes:
                    code_string += code + ", "
            code_string = code_string[:-2]
            variable_query = "select {} from acs_data where county = '{}'".format(code_string, county)
            variable_query_results = db.execute(variable_query).fetchall()

            if len(variable_query_results) > 0:
                    variable_values = variable_query_results[0]
                    for i in xrange(len(variable_values)):
                            # checks if value is not available for this county, if not available will return empty string
                            if variable_values[i] != '':
                                    weighted_sums[i] += float(variable_values[i])*county_pop

    # If no county information found for county_list, return array of 'n/a'
    if total_pop == 0:
            return ['n/a' for var in variable_codes]
    else:
            return [str(s/total_pop) for s in weighted_sums]

# ARGUMENTS: raw uploaded CSV file, array of variable code names in string form
# OUTPUT: updated CSV with new variables appended, **IN STRING FORM**
def append_variables(csv_file, variable_codes):
	db = sqlite3.connect('acs/acs.db') # opens the ACS db
	index_of_zip = None # the cell index of the ZIP column
        error = '' # empty string for now

	# reads in csv as array of arrays
	array_of_arrays = []
	for row in csv.reader(csv_file):
		array_of_arrays.append(row)
	
	# modifies csv in place to append extra column
	for row_index in xrange(len(array_of_arrays)):
		if row_index == 0: 
			# checks if the first/second row is labled with some variation of 'zip', saves that index
			row = array_of_arrays[row_index]
			for cell_index in xrange(len(row)):
				if row[cell_index].lower() in ['zip', 'zip_code', 'zipcode', 'zip-code', 'zipcodes', 'zip_codes', 'zip-codes']:
					index_of_zip = cell_index
					break

			# appends variable names of desired variable codes to the first row
			if index_of_zip != None:
				for code in variable_codes:
					array_of_arrays[row_index].append(ACS_VARIABLES[code])

		        else:
			    error = 'First row of file: did not find column for zipcode\n'
                            break
                
                else:
			zip_code = str(array_of_arrays[row_index][index_of_zip])
                        if len(zip_code) < 5:
                                for _ in xrange(5-len(zip_code)): zip_code = '0' + zip_code # add 0s to beginning of county code if needed

			county_query = "select county from county_zip where zip = '{}'".format(zip_code)
			county_query_results = db.execute(county_query).fetchall()

			if len(county_query_results) > 0:
				# HACKY HACKY HACKY - only using first county, missing 0s for some county codes, adding them manually
                                county_list = []
                                for county_query in county_query_results:
                                        county = str(county_query[0])
                                        if len(county) < 5:
                                                for _ in xrange(5-len(county)): county = '0' + county # add 0s to beginning of county code if needed
                                        county_list.append(county)
                                # append variable values for the given row
                                variable_values = weighted_averages(db, variable_codes, county_list)
                                for val in variable_values:
				        array_of_arrays[row_index].append(val)
                                '''
                                for code in variable_codes:
					variable_query = "select {} from acs_data where county = '{}'".format(code, county)
					variable_query_results = db.execute(variable_query).fetchall()

					if len(variable_query_results) > 0:
						# HACKY HACKY HACKY - just using first results for a county
						variable_value = str(variable_query_results[0][0])
						array_of_arrays[row_index].append(variable_value)
                                        else:
                                                error = "Row {}: did not find variable '{}' for county {}".format(row_index, zip_code, county)
                                                '''
                        else:
                                error = "Row {}: did not find county codes for zip code {}".format(row_index, zip_code)

	# closes the db after usage
	db.close()

	# converts modified csv into string for outputting
	csv_string = ''
	for row in array_of_arrays:
		# if a row contains a cell whose contents contain a comma,
		# surround that cell with an extra layer of quotes so the extra comma isn't mistaken for a delimiter
		for i in xrange(len(row)):
			if ',' in row[i]:
				row[i] = '"' + row[i] + '"'

		row_string = ','.join(row)
		csv_string += row_string + '\n'

	return [csv_string, error]

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
