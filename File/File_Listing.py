##############################################################
#                     List File with Metadata                #
##############################################################
import os
import sys
import logging
import csv
import sqlite3
import argparse
import datetime

def main():
    #Define system argument
    parser = argparse.ArgumentParser(description='List File with Metadata',
                                     epilog='Developed in Python')
    parser.add_argument('CUSTODIAN', help='Name of custodian collection')
    parser.add_argument('DB_PATH', help='File path and name of database file')
    parser.add_argument('--input', help='Base directory to scan')
    parser.add_argument('--output', help='Output file to write to CSV and HTML')
    parser.add_argument('-L', help='File path and name of log file.')
    args = parser.parse_args()

    custodian = args.CUSTODIAN
    db = args.DB_PATH

    #Check the input and output location
    if args.input:
        source = ('input', args.input)
    elif args.output:
        source = ('output', args.output)
    else:
        raise argparse.ArgumentError('Please specify input or output')

    #Set up system log
    if args.L:
        if not os.path.exists(args.L):
            os.makedirs(args.L)
        log_path = os.path.join(args.L, 'file_list.log')
    else:
        log_path = 'file_list.log'
    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s', filemode='a')

    #Enter log information
    logging.info('Starting File Listing')
    logging.debug('System ' + sys.platform)
    logging.debug('Version ' + sys.version)

    #Initialize SQLite database
    logging.info('Initiating SQLite database: ' + db)
    conn = initDB(db)
    cur = conn.cursor()
    logging.info('Initialization Successful')

    #Obtain custodian ID
    logging.info('Retrieving or adding custodian: ' + custodian)
    custodian_id = getOrAddCustodian(cur, custodian)
    while not custodian_id:
        custodian_id = getOrAddCustodian(cur, custodian)
    logging.info('Custodian Retrieved')
    if source[0] == 'input':
        logging.info('Ingesting base input directory: ' + source[1])
        ingestDirectory(cur, source[1], custodian_id)
        conn.commit()
        logging.info('Ingest Complete')
    elif source[0] == 'output':
        logging.info('Preparing to write output: ' + source[1])
        writeOutput(cur, source[1], custodian)
    else:
        raise argparse.ArgumentError('Could not interpret run time arguments')

    cur.close()
    conn.close()
    logging.info('Script Completed')


def initDB(db_path):
    if os.path.exists(db_path):
        logging.info('Existing Database Found')
        return sqlite3.connect(db_path)
    else:
        logging.info('Initializing New Database')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        sql = 'CREATE TABLE Custodians (id INTEGER PRIMARY KEY, name TEXT);'
        cur.execute(sql)
        cur.execute('PRAGMA foreign_keys = 1;')
        sql = "CREATE TABLE Files(id INTEGER PRIMARY KEY, custodian INTEGER REFERENCES Custodians(id), file_name TEXT, file_path TEXT, extension TEXT, file_size INTEGER, mtime TEXT, ctime TEXT, atime TEXT, mode INTEGER, inode INTEGER);"
        cur.execute(sql)
        return conn


def getOrAddCustodian(cur, custodian):
    #Obtain Custodian ID
    id = getCustodian(cur, custodian)
    #Create a New Custodian Record while It does not Exist
    if id:
        return id[0]
    else:
        sql = "INSERT INTO Custodians (id, name) VALUES (null, '" + custodian + "') ;"
        cur.execute(sql)
        return None


def getCustodian(cur, custodian):
    #Obtain Custodian ID based on Custodian Name
    sql = "SELECT id FROM Custodians WHERE name='{}';".format(custodian)
    cur.execute(sql)
    data = cur.fetchone()
    return data


def ingestDirectory(cur, source, custodian_id):
    count = 0
    for root, folders, files in os.walk(source):
        for file_name in files:
            meta_data = dict()
            try:
                meta_data['file_name'] = file_name
                meta_data['file_path'] = os.path.join(root, file_name)
                meta_data['extension'] = os.path.splitext(file_name)[-1]

                file_stats = os.stat(meta_data['file_path'])
                #Record File Mode and Permission
                meta_data['mode'] = oct(file_stats.st_mode)
                #Record Inode Value
                meta_data['inode'] = int(file_stats.st_ino)
                #Record File Size
                meta_data['file_size'] = int(file_stats.st_size)
                #Record Access Time
                meta_data['atime'] = formatTimestamp(file_stats.st_atime)
                #Record Modification Time
                meta_data['mtime'] = formatTimestamp(file_stats.st_mtime)
                #Record Creating Time
                meta_data['ctime'] = formatTimestamp(file_stats.st_ctime)
            except Exception as e:
                logging.error('No data available for: ' + meta_data['file_path'] + e.__str__())
            meta_data['custodian'] = custodian_id
            columns = '","'.join(meta_data.keys())
            values = '","'.join(str(x).encode('string_escape') for x in meta_data.values())
            sql = 'INSERT INTO Files ("' + columns + '") VALUES ("' + values + '")'
            cur.execute(sql)
            count += 1

    logging.info('Stored meta data for ' + str(count) + ' files')


def formatTimestamp(timestamp):
    date_time = datetime.datetime.fromtimestamp(timestamp)
    date_time_format = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return date_time_format


def writeOutput(cur, source, custodian):
    custodian_id = getCustodian(cur, custodian)

    if custodian_id:
        custodian_id = custodian_id[0]
        sql = "SELECT COUNT(id) FROM Files where custodian = '" + str(custodian_id) + "'"
        cur.execute(sql)
        count = cur.fetchone()
    else:
        logging.error('Custodian not found in database')

    if not count or not count[0] > 0:
        logging.error('Files not found for custodian')
    elif source.endswith('.csv'):
        writeCSV(cur, source, custodian_id)
    elif source.endswith('.html'):
        writeHTML(cur, source, custodian_id, custodian)
    elif not (source.endswith('.html')or source.endswith('.csv')):
        logging.error('Could not determine file type')
    else:
        logging.error('Unknown Error Occurred')


def writeCSV(cur, source, custodian_id):
    sql = "SELECT * FROM Files where custodian = '" + str(custodian_id) + "'"
    cur.execute(sql)

    column_names = [description[0] for description in cur.description]
    logging.info('Writing CSV report')
    csv_file = open(source, 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(column_names)

    for entry in cur.fetchall():
        csv_writer.writerow(entry)
    csv_file.flush()
    logging.info('CSV report completed: ' + source)


def writeHTML(cur, source, custodian_id, custodian_name):
    sql = "SELECT * FROM Files where custodian = '" + str(custodian_id) + "'"
    cur.execute(sql)

    column_names = [description[0] for description in cur.description]
    table_header = '</th><th>'.join(column_names)
    table_header = '<tr><th>' + table_header + '</th></tr>'

    logging.info('Writing HTML report')

    html_file = open(source, 'w')
    html_string = "<html><body>\n"
    html_string += '<link rel="stylesheet" href="style.css">\n'
    html_string += "<h1>File Listing for Custodian ID: " + str(custodian_id) + ", " + custodian_name + "</h1>\n"
    html_string += "<table class='table table-hover table-striped'>\n"
    html_file.write(html_string)
    html_file.write(table_header)

    for entry in cur.fetchall():
        row_data = "</td><td>".join([str(x).encode('utf-8') for x in entry])
        html_string = "\n<tr><td>" + row_data + "</td></tr>"
        html_file.write(html_string)
        html_file.flush()
    html_string = "\n</table>\n</body></html>"
    html_file.write(html_string)
    logging.info('HTML Report completed: ' + source)


if __name__ == '__main__':
    main()
