#!/usr/bin/env python
import sys
import DataHelper #local helper file

sys.path.insert(0, 'lib')
from flask import Flask, Response, render_template, request
from werkzeug import secure_filename

app = Flask(__name__)

@app.route('/home')
def home():
	return render_template('index.html')

#TODO: HANDLE RAISES/TRY-EXCEPT BLOCKS
#TODO: UNICODE STUFF? ALSO MIGHT ASCII ERROR IF NO STR() WRAPPER AROUND APPENDED DATA
#TODO: SANITIZE SQL: https://docs.python.org/2/library/sqlite3.html
#TODO: this tool will rewrite the CSV file from scratch, could clear some Excel formatting stuff
#TODO: CHECK VALID ZIP? / ZIP CODES WITH LEADING ZEROES / COUNTY CODES WITH LEADING ZEROES / HACKY STUFF
#TODO: CHECK IF APPENDED DATA IS EVEN CORRECT
#TODO: FEEDBACK WHEN FILETYPE IS INCORRECT
#TODO: SELECTING VARIABLES TO APPEND
#TODO: INSTRUCTIONS
#TODO: TRIM /LIB STUFF?
#TODO: somehow app.cgi's permissions need to be reset every time upload to AFS
#TODO: SUEXECD STUFF?
#TODO: MAYBE COMPARE OUTPUT TO INPUT AS SANITY CHECK?
#TODO: ASSUMES COMMAS AS DELIMITERS
#TODO: PROCESSING METER?
#TODO: FILLED IN DATA SEEMS RATHER SPARSE?
@app.route('/index', methods=['GET', 'POST'])
def append():
	# display template for submitting CSV
	if request.method == 'GET':
		return render_template('index.html')

	# logic for manipulating submitted CSV and outputting
	elif request.method == 'POST':
		input_file = request.files['input_file']
		acs_variable_codes = ['B03002_001E', 'B03002_003E']
		# acs_variable_codes = request.files['acs_variable_codes']

		# checks if inputs exist
		if not input_file or not acs_variable_codes or len(acs_variable_codes) == 0:
			# HANDLE EXCEPTION
			raise 'INPUT ERROR'

		# checks if input is a CSV
		if DataHelper.allowed_file(input_file.filename):
			output_csv_string = ''
			try:
				output_csv_string = DataHelper.append_variables(input_file, acs_variable_codes)
			except Exception, e:
				# HANDLE EXCEPTION
				print e
				raise

			# sanitizes filename
			output_filename = 'APPENDED-' + secure_filename(input_file.filename)

			# prepares appended CSV file to be downloaded to user
			output = Response(
					output_csv_string,
					mimetype='text/csv',
					headers={ 'Content-disposition': 'attachment; filename=' + output_filename }
					)
			return output
		else:
			# NOT VALID FILE TYPE
			raise

if __name__ == '__main__':
	app.run(debug=True)