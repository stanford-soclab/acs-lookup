################################################
# DATAHELPER MODULE FOR ACS_LOOKUP.PY FLASK APP
################################################
import csv, sqlite3 
from collections import OrderedDict

# checks if filename is .csv
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] == 'csv'

# ARGUMENTS: list of variables, database
# OUTPUT: dictionary of variable to table that it's contained in 
def var_to_table(variable_codes, db):
        varlist_dict = {}
        for table in ['acs1','acs2','acs3','acs4','acs5','acs6','acs7','acs8','acs9','acs10']:
                query = db.execute('pragma table_info({})'.format(table))
                col_names = [col[1] for col in query]
                var_in_table = [var for var in variable_codes if var in col_names]
                for var in var_in_table:
                        varlist_dict[var] = table
        return varlist_dict


# ARGUMENTS: database, list of variables, list of counties
# OUTPUT: list of weighted averages for variables, weighted over list of counties by total population of each county
def weighted_averages(db, variable_codes, county_list, var_table_dict):
        result = []
        # Calculate weighted average for each variable
        for code in variable_codes:
                total_pop, weighted_sum = 0, 0
                for county in county_list:
                        # Add population of county to total_pop
                        pop_query = "select B01003_001E from acs2 where county = '{}'".format(county)
                        #TODO: figure out whether ACS db now just has zipcode information, and whether we still need weighted average
                        pop_query_results = db.execute(pop_query).fetchall()
                '''
                        variable_query = "select {} from {} where county = '{}'".format(code, var_table_dict[code], county)
                        variable_query_results = db.execute(variable_query).fetchall()
                        if len(pop_query_results) > 0 and len(variable_query_results) > 0: # If no data on county, skip
                                county_pop, var_val = pop_query_results[0][0], variable_query_results[0][0]
                                if county_pop != '' and var_val != '': # If either population or variable value is missing, ignore
                                        total_pop += float(county_pop)
                                        weighted_sum += float(county_pop)*float(var_val)
                                        
                if total_pop != 0: # If at least one county had non-empty variable value
                        result.append(str(int(weighted_sum/total_pop))) # Round weighted average to nearest int
                else:
                        result.append("n/a")
                        '''
        return result


# ARGUMENTS: csv file of variable code and name pairs
# OUTPUT: dict of variable names to codes
def create_labelcode_dict(csv_file):
        labelcode_pairs = []
        with open(csv_file, 'rb') as f:
                labels_csv = csv.reader(f)
                for row in labels_csv:
                        labelcode_pairs.append((row[0], row[1]))
        return OrderedDict(labelcode_pairs)
                                 

# dict of ACS codes to English fields; uses OrderedDict so the options appear in order on selection box
ACS_VARIABLES = create_labelcode_dict('acs_new/parent_codes_names.csv')
ACS_CHILD_VARIABLES = create_labelcode_dict('acs_new/codes_names.csv')


# ARGUMENTS: list of parent variable codes from parent_codes_names.csv
# OUTPUT: list of child variables with that parent variable code from codes_names.csv
def collect_child_variables(variable_codes):
        result = []
        for parent_code in variable_codes:
                for child_code in ACS_CHILD_VARIABLES.keys():
                        if parent_code in child_code:
                                result.append(child_code)
        return result


# ARGUMENTS: raw uploaded CSV file, array of variable code names in string form
# OUTPUT: updated CSV with new variables appended, **IN STRING FORM**
def append_variables(csv_file, variable_codes):
	db = sqlite3.connect('acs_new/acs_data/acs_db') # opens the ACS db
	index_of_zip = None # the cell index of the ZIP column
        error = '' # empty string for now, TODO track errors somehow
        child_variable_codes = collect_child_variables(variable_codes)
        var_table_dict = var_to_table(child_variable_codes, db) # creates dict of variable code to table it is contained in

	# reads in csv as array of arrays
	array_of_arrays = []
	for row in csv.reader(csv_file):
		array_of_arrays.append(row)
	# modifies csv in place to append extra column
	for row_index in xrange(len(array_of_arrays)):
                # First row
		if row_index == 0: 
                        row = array_of_arrays[row_index]
                        for cell_index in xrange(len(row)):
                                if row[cell_index].lower() in ['zip', 'zip_code', 'zipcode', 'zip-code', 'zipcodes', 'zip_codes', 'zip-codes']:
                                        index_of_zip = cell_index
                                        break

                        # appends variable names of desired variable codes to the first row
                        if index_of_zip != None:
                                for code in child_variable_codes:
                                        array_of_arrays[row_index].append(ACS_CHILD_VARIABLES[code])
                        else:
                                error = 'First row of file: did not find column for zipcode\n'
                                break
                # Other rows
                else:
			zip_code = str(array_of_arrays[row_index][index_of_zip])
                        # Remove extra zeroes from beginning of zip code
                        while zip_code[0] == '0':
                                zip_code = zip_code[1:] 
			county_query = "select county from county_zip where zip = '{}'".format(zip_code)
			county_query_results = db.execute(county_query).fetchall()

			if len(county_query_results) > 0:
                                county_list = []
                                for county_query in county_query_results:
                                        county = str(county_query[0])
                                        if len(county) < 5:
                                                for _ in xrange(5-len(county)): county = '0' + county # add 0s to beginning of county code if needed
                                        county_list.append(county)
                                # append variable values for the given row
                                variable_values = weighted_averages(db, child_variable_codes, county_list, var_table_dict)
                                for val in variable_values:
				        array_of_arrays[row_index].append(val)
                        else:
                                error = "Row {}: did not find county codes for zip code {}".format(row_index, zip_code)
	'''
'''
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


'''
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
'''
