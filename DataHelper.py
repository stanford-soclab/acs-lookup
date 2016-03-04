################################################
# DATAHELPER MODULE FOR ACS_LOOKUP.PY FLASK APP
################################################
import csv
import sqlite3

# checks if filename is .csv
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] == 'csv'

# ARGUMENTS: raw uploaded CSV file, array of variable code names in string form
# OUTPUT: updated CSV with new variables appended, **IN STRING FORM**
def append_variables(csv_file, variable_codes):
	db = sqlite3.connect('acs/acs.db') # opens the ACS db
	index_of_zip = None # the cell index of the ZIP column

	# reads in csv as array of arrays
	array_of_arrays = []
	for row in csv.reader(csv_file):
			array_of_arrays.append(row)
	
	# modifies csv in place to append extra column
	for row_index in xrange(len(array_of_arrays)):
		if row_index == 0:
			# checks if the first row is labled with some variation of 'zip', saves that index
			row = array_of_arrays[row_index]
			for cell_index in xrange(len(row)):
				if row[cell_index].lower() in ['zip', 'zip_code', 'zipcode', 'zip-code', 'zipcodes', 'zip_codes', 'zip-codes']:
					index_of_zip = cell_index
					break

			assert index_of_zip != None, 'ZIP COLUMN NOT FOUND'

			# appends variable names of desired variable codes to the first row
			for code in variable_codes:
				array_of_arrays[row_index].append(ACS_VARIABLES[code])

		else:
			assert index_of_zip != None, 'ZIP COLUMN ERROR'

			zip_code = array_of_arrays[row_index][index_of_zip]

			county_query = "select county from county_zip where zip = '{}'".format(zip_code)
			county_query_results = db.execute(county_query).fetchall()

			if len(county_query_results) > 0:
				# HACKY HACKY HACKY
				county = str('0' + county_query_results[0][0])

				# append variable values for the given row
				for code in variable_codes:
					variable_query = "select {} from acs_data where county = '{}'".format(code, county)
					variable_query_results = db.execute(variable_query).fetchall()

					if len(variable_query_results) > 0:
						# HACKY HACKY HACKY
						variable_value = str(variable_query_results[0][0])
						array_of_arrays[row_index].append(variable_value)

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

	return csv_string

# dict of ACS codes to English fields
ACS_VARIABLES = {
	'B03002_001E': 'Hispanic Or Latino Origin By Race Total',
	'B03002_003E': 'White Alone',
	'B03002_004E': 'Black Or African American Alone',
	'B03002_012E': 'Hispanic Or Latino',
	'B05012_001E': 'Nativity In The United States',
	'B05012_003E': 'Nativity In The United States (Foreign-Born)',
	'B01003_001E': 'Total Population',
	'B05001_001E': 'Nativity And Citizenship Status In The United States Total',
	'B05001_006E': 'Nativity and Citizenship Status In The United States (Non-Citizen)',
	'B17001_001E': 'Poverty Status In The Past 12 Months Total',
	'B17001_002E': 'Income In The Past 12 Months Below Poverty Level',
	'B17001A_002E': 'Poverty Status In The Past 12 Months Total (White Alone)',
	'B17001A_001E': 'Income In The Past 12 Months Below Poverty Level (White Alone)',
	'B17001B_002E': 'Poverty Status In The Past 12 Months Total (Black Or African American Alone)',
	'B17001B_001E': 'Income In The Past 12 Months Below Poverty Level (Black Or African American Alone)',
	'B17001I_002E': 'Poverty Status In The Past 12 Months Total (Hispanic Or Latino)',
	'B17001I_001E': 'Income In The Past 12 Months Below Poverty Level (Hispanic Or Latino)',
	'B19013_001E': 'Median Household Income In The Past 12 Months',
	'B19013A_001E': 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (White Alone Householder)',
	'B19013B_001E': 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Black Or African American Alone Householder)',
	'B19013I_001E': 'Median Household Income In The Past 12 Months (In 2012 Inflation-Adjusted Dollars) (Hispanic Or Latino Householder)',
	'B19051_001E': 'Earnings In The Past 12 Months For Households Total',
	'B01002_001E': 'Median Age By Sex Total',
	'B23025_001E': 'Employment Status For The Population 16 Years And Over Total',
	'B23025_005E': 'Unemployed',
	'B23025_003E': 'Civilian Labor Force',
	'B19083_001E': 'Gini'
}