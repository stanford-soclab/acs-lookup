import sys

def format_string(word):
    return '"' + word + '"'

def parse_acs(data):
    file_name = data.split('.')[0] + '.dat'
    dat_file = open(file_name, 'w')
    counties = set()

    with open(data) as f:
        for line in f:
            row = line.replace('\n', '').split('\t')
            row = [format_string(word) for word in row]
            
            if row[0] == '"GEOID"':
                continue

            county = row[2]
            B03002_001E = row[3]
            B03002_003E = row[5]
            B03002_004E = row[7]
            B03002_012E = row[9]
            B05012_001E = row[12]
            B05012_003E = row[14]
            B01003_001E = row[16]
            B05001_001E = row[18]
            B05001_006E = row[20]
            B17001_001E = row[22]
            B17001_002E = row[24]
            B17001A_002E = row[26]
            B17001A_001E = row[28]
            B17001B_002E = row[30]
            B17001B_001E = row[32]
            B17001I_002E = row[34]
            B17001I_001E = row[36]
            B19013_001E = row[38]
            B19013A_001E = row[40]
            B19013B_001E = row[42]
            B19013I_001E = row[44]
            B19051_001E = row[46]
            B01002_001E = row[48]
            B23025_001E = row[50]
            B23025_005E = row[52]
            B23025_003E = row[54]
            B19083_001E = row[56]

            dat_file.write('|'.join([
               county,
               B03002_001E,
               B03002_003E,
               B03002_004E,
               B03002_012E,
               B05012_001E,
               B05012_003E,
               B01003_001E,
               B05001_001E,
               B05001_006E,
               B17001_001E,
               B17001_002E,
               B17001A_002E,
               B17001A_001E,
               B17001B_002E,
               B17001B_001E,
               B17001I_002E,
               B17001I_001E,
               B19013_001E,
               B19013A_001E,
               B19013B_001E,
               B19013I_001E,
               B19051_001E,
               B01002_001E,
               B23025_001E,
               B23025_005E,
               B23025_003E,
               B19083_001E
            ]) + '\n')

def parse_county(data):
    file_name = data.split('.')[0] + '.dat'
    dat_file = open(file_name, 'w')

    with open(data) as f:
        for line in f:
            row = line.replace('\r', '').replace('\n', '').split(',')
            row = [format_string(word) for word in row]

            if row[0] == '"zip"':
                continue

            zipcode = row[0].zfill(5)
            county = row[1]
            population = row[2]

            dat_file.write('|'.join([
                zipcode,
                county,
                population
            ]) + '\n')

def main(argv):
    # usage: python parse.py acs_data.asc county_zip.csv
    acs_data = argv[1]
    parse_acs(acs_data)

    county_data = argv[2]
    parse_county(county_data);

if __name__ == '__main__':
    main(sys.argv)
