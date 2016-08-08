##############################################################
#                     Bitcoin Address Lookup                 #
#       Blockchain Browser: https://blockchain.info/         #
# Blockchain API: https://blockchain.info/api/blockchain_api #
##############################################################
import argparse
import json
import logging
import urllib2
import time_converter
import sys
import csv
import os

def main():
    #Define system argument
    parser = argparse.ArgumentParser(description='Bitcoin Address Lookup',
                                     epilog='Developed in Python ')
    parser.add_argument('BTCADDRESS', help='Bitcoin Address')
    parser.add_argument('OUTPUT', help='Output CSV file')
    parser.add_argument('-L', help='Specify log directory')
    args = parser.parse_args()

    address = args.BTCADDRESS
    output_dir = args.OUTPUT

    #Set up Log
    if args.L:
        if not os.path.exists(args.L):
            os.makedirs(args.L)
        log_path = os.path.join(args.L, 'btc_address_lookup.log')
    else:
        log_path = 'btc_address_lookup.log'
    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s', filemode='w')
    logging.info('Starting Bitcoin Address Lookup')
    logging.debug('System Platform: ' + sys.platform)
    logging.debug('System Version: ' + sys.version)
    logging.info('Initiated program for Bitcoin address: %s' % (address))
    logging.info('Obtaining JSON structured data from blockchain.info')

    print '*'*40
    print 'Bitcoin Address Lookup'
    print '*'*40

    #Load account and print information
    raw_account = getAddress(address)
    account = json.loads(raw_account.read())
    printHeader(account)
    parseTransactions(account, output_dir)


def getAddress(address):
    #Open the blockchain browser page and return the content
    url = 'https://blockchain.info/address/'+address+'?format=json'
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError, e:
        logging.error('URL Error for %s' % (url))
        if hasattr(e, 'code') and hasattr(e, 'headers'):
            logging.debug('%s: %s' % (e.code, e.reason))
            logging.debug('%s' % (e.headers))
        print 'Received URL Error for Blockchain Browser: %s' % url
        logging.info('Program exiting...')
        sys.exit(1)

def parseTransactions(account, output_dir):
    msg = 'Parsing account and transaction information...'
    logging.info(msg)
    print msg
    transactions = []
    for i, tx in enumerate(account['txs']):
        transaction = []
        outputs = {}
        inputs = getInputs(tx)
        transaction.append(i)
        transaction.append(time_converter.time_converter(tx['time']))
        transaction.append(tx['hash'])
        transaction.append(inputs)
        for output in tx['out']:
            outputs[output['addr']] = output['value'] * 10**-8
        transaction.append('\n'.join(outputs.keys()))
        transaction.append('\n'.join(str(v) for v in outputs.values()))
        transaction.append('%.8f' % (sum(outputs.values())))
        transactions.append(transaction)
    csvWriter(transactions, output_dir)


def printHeader(account):
    print 'Address:', account['address']
    print 'Current Balance: %.8f BTC' % (account['final_balance'] * 10**-8)
    print 'Total Sent: %.8f BTC' % (account['total_sent'] * 10**-8)
    print 'Total Received: %.8f BTC' % (account['total_received'] * 10**-8)
    print 'Number of Transactions:', account['n_tx']
    print '*'*40


def getInputs(tx):
    inputs = []
    for input_addr in tx['inputs']:
        inputs.append(input_addr['prev_out']['addr'])
    if len(inputs) > 1:
        input_string = '\n'.join(inputs)
    else:
        input_string = ''.join(inputs)
    return input_string

def csvWriter(data, output_dir):
    logging.info('Writing transactions into %s' % (output_dir))
    print 'Writing transactions....'
    headers = ['Index', 'Date', 'Transaction Hash', 'Inputs', 'Outputs', 'Values', 'Total']
    try:
        csvfile = open(output_dir, 'wb')
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for transaction in data:
            writer.writerow(transaction)
        csvfile.flush()
        csvfile.close()
    except IOError, e:
        logging.error('Error writing transactions to %s' % (e.filename))
        logging.error('Generated message: %s' % (e.strerror))
        print 'Error found in writing to CSV file'
        logging.info('Program exiting.')
        sys.exit(1)
    logging.info('Program exiting.')
    print 'Program exiting.'
    sys.exit(0)

if __name__ == '__main__':
    main()
