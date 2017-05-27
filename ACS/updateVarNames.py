'''
updateVarNames.py

creates new csv of variable code and name pairs with parent variable names added to variable names 
'''

import csv
import sys
sys.path.insert(0, '..')
import DataHelper

with open('codes_names.csv', 'rb') as f: # open list of variable code and name pairs
        labels_csv = csv.reader(f)
        
        with open('codes_names_new.csv', 'wb') as nf: # open new file for updated list of variable code and name pairs
                labels_csv_new = csv.writer(nf)
                parent_codes_names = DataHelper.labels_to_codes('parent_codes_names.csv') #TODO: gotta update parent_codes csv to only contain important parents

                # update each line in original csv and add to new csv
                for row in labels_csv:
                        var_code = row[0][:6] 
                        print var_code
                        if var_code in parent_codes_names:
                                var_name = parent_codes_names[var_code] 
                                newline = [row[0], var_name + ':!!' + row[1]]
                                labels_csv_new.writerow(newline)
