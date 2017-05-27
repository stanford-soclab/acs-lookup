'''
updateVarNames.py

Creates new csv of variable code and name pairs with parent variable names added to variable names 
'''

import csv
import sys
sys.path.insert(0, '..')
import DataHelper

file_name = sys.argv[1]
with open(file_name, 'rb') as f: # open list of variable code and name pairs
        labels_csv = csv.reader(f)
        
        with open('codes_names_new.csv', 'wb') as nf: # open new file for updated list of variable code and name pairs
                labels_csv_new = csv.writer(nf)
                parent_codes_names = DataHelper.create_labelcode_dict('parent_codes_names.csv') 

                # update each line in original csv and add to new csv
                for row in labels_csv:
                        var_code = row[1].split('_')[0] 
                        if var_code in parent_codes_names:
                                var_name = parent_codes_names[var_code] 
                                extended_varname = var_name + ':!!' + row[2]
                                        
                                newline = [row[1], extended_varname]
                                if row[1] == 'B01001H_002E': 
                                        print extended_varname
                                        print newline
                                labels_csv_new.writerow(newline)
