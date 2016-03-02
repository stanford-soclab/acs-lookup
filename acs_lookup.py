#!/usr/bin/env python
import sqlite3
import sys
import csv

sys.path.insert(0, 'lib')
from flask import Flask, Response, render_template, request, make_response

app = Flask(__name__)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] == 'csv'

@app.route('/home')
def home():
	return render_template('index.html')

@app.route("/hello")
def hello():
	db = sqlite3.connect('acs/acs.db')
	for county in db.execute("select county from county_zip where zip = '94305'"):
		return county[0]
	return "Hello World!"

@app.route('/acs_append', methods=['GET', 'POST'])
def acs_append():
	if request.method == 'GET':
		return render_template('acs_append.html')
	elif request.method == 'POST':
		input_file = request.files['input_file']
		data_reader = csv.reader(input_file)
		data = []
		for row in data_reader:
				data.append(row)

		output_string = ''
		for row in data:
			row_string = ','.join(str(cell) for cell in row)
			output_string += row_string + '\n'

		output = Response(
				output_string,
				mimetype="text/csv",
				headers={"Content-disposition":
								 "attachment; filename=myplot.csv"})
		return output

if __name__ == '__main__':
	app.run()