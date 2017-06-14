################################################
# DATAHELPER MODULE FOR ACS_LOOKUP.PY FLASK APP
################################################
import csv, sqlite3, numpy
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
ACS_VARIABLES = create_labelcode_dict('ACS/parent_codes_names.csv')
ACS_CHILD_VARIABLES = create_labelcode_dict('ACS/codes_names.csv')


# ARGUMENTS: list of parent variable codes from parent_codes_names.csv
# OUTPUT: list of child variables with that parent variable code from codes_names.csv
def collect_child_variables(variable_codes):
        result = []
        for parent_code in variable_codes:
                for child_code in ACS_CHILD_VARIABLES.keys():
                        if parent_code == child_code.split('_')[0]:
                                result.append(child_code)
        return result

# ARGUMENTS: list of variable codes, variable to table dictionary
# OUTPUT: sqlite query for all variables 
def create_query(child_variable_codes, var_table_dict):
        query = 'select acs1.zip,'
        tables_used = ['acs1']
        for var in child_variable_codes:
                var_table = var_table_dict[var]
                query += ' {}.{},'.format(var_table, var)
                if var_table not in tables_used:
                        tables_used.append(var_table)
        query = query[:-1]
        query += ' from'
        for table in tables_used:
                query += ' {},'.format(table)
        query = query[:-1]
        if len(tables_used) > 1:
                query += ' where'
                for table in tables_used[1:]:
                        query += ' {}.zip = {}.zip and'.format(tables_used[0], table)
                query = query[:-4]
        query += ';'
        return query

# ARGUMENTS: raw uploaded CSV file, array of variable code names in string form
# OUTPUT: updated CSV with new variables appended, **IN STRING FORM**
def append_variables(csv_file, variable_codes):
	db = sqlite3.connect('ACS/acs_data/acs_db') # opens the ACS db
	index_of_zip = None # the cell index of the ZIP column
        error = '' # empty string for now, TODO track errors somehow
        child_variable_codes = collect_child_variables(variable_codes)
        var_table_dict = var_to_table(child_variable_codes, db) # creates dict of variable code to table it is contained in

	# reads in csv as array of arrays
	array_of_arrays = []
	for row in csv.reader(csv_file):
		array_of_arrays.append(row)
	# modifies csv in place to append extra column
        query = create_query(child_variable_codes, var_table_dict)
        c = db.cursor()
        c.execute(query)
        query_table = []
        for row in c:
                query_table.append(row)
        zip_list = [row[0] for row in query_table]
        for row_index in xrange(len(array_of_arrays)):
                array_of_arrays[row_index].append('') # Add blank column for aesthetic purposes
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
                        try:
                                # Remove extra zeroes from beginning of zip code
                                while zip_code[0] == '0':
                                        zip_code = zip_code[1:] 
                                zip_row_index = zip_list.index(zip_code)
                                for var in query_table[zip_row_index][1:]:
                                        if str(var) == '':
                                                array_of_arrays[row_index].append('n/a')
                                        else:
                                                array_of_arrays[row_index].append(str(var))
                        except:
                                array_of_arrays[row_index].append('Zipcode missing')
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

