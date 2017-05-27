#!/usr/bin/ruby
require 'sqlite3'

$db = SQLite3::Database.open('acs.db')

def append_variables(csv_file, variable)
    file_name = csv_file.split('.')[0] + '_output.csv'
    output = open(file_name, 'w+')
    input = open(csv_file, 'r')

    input.each_line do |line|
    	zip = line.split(',')[0]
    	query = 'select county from county_zip where zip = "' + zip + '"'
    	county = $db.execute query
    	query = 'select ' + variable + ' from acs_data where county = ' + county[0]
    	result = $db.execute query
    	puts result
    end
end

# usage: ruby append.rb data.csv variable1 variable2 ...  
csv_file = ARGV[0]
variable = ARGV[1]
append_variables(csv_file, variable)

$db.close if $db
    